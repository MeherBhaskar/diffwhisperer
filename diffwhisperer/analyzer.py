"""
Git utilities for analyzing changes and generating commit messages using AI.
"""

from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter
import git
import google.generativeai as genai


class DiffAnalyzer:
    COMMIT_TYPES = ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'build', 'ci', 'chore']
    
    def __init__(self, repo_path: str = ".", api_key: str = None, model_name: str = "gemini-2.0-flash"):
        """
        Initialize the DiffAnalyzer.
        
        Args:
            repo_path: Path to the git repository
            api_key: Google API key. If not provided, will try to get from environment variable.
            model_name: Name of the Gemini model to use (default: gemini-2.0-flash)
        """
        self.repo = git.Repo(repo_path)
        if api_key:
            genai.configure(api_key=api_key)
        
        try:
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            available_models = [m.name for m in genai.list_models()]
            raise ValueError(f"Invalid model name: {model_name}. Available models: {', '.join(available_models)}") from e
            
    def _determine_scope(self, changed_files: List[str]) -> str:
        """Determine the commit scope from changed files."""
        if not changed_files:
            return "misc"
            
        # Extract top-level directories
        dirs = [Path(f).parts[0] if len(Path(f).parts) > 1 else "misc" for f in changed_files]
        
        # Find most common directory
        counts = Counter(dirs)
        return counts.most_common(1)[0][0]
        
    def _prepare_diff_summary(self, staged_changes: Dict[str, str]) -> str:
        """Prepare a concise summary of the changes."""
        summary_parts = []
        for file_path, diff in staged_changes.items():
            # Get just the filename without path
            filename = Path(file_path).name
            
            # Count number of changed lines
            lines = diff.split('\n')
            added = len([l for l in lines if l.startswith('+')])
            removed = len([l for l in lines if l.startswith('-')])
            
            summary = f"File: {filename}"
            if added or removed:
                summary += f" ({added} added, {removed} removed)"
                
            # Add first 2-3 lines of actual changes as context
            change_lines = [l for l in lines if l.startswith('+') or l.startswith('-')][:3]
            if change_lines:
                summary += "\nChanges:\n" + "\n".join(change_lines)
                
            summary_parts.append(summary)
            
        return "\n\n".join(summary_parts)

    def get_staged_changes(self) -> Dict[str, str]:
        """Get all staged changes in the repository."""
        staged_files = {}
        
        # Get staged differences
        diff = self.repo.index.diff("HEAD")
        
        # Also include newly created files
        diff.extend(self.repo.index.diff(None))
        
        for diff_item in diff:
            if diff_item.a_path:
                staged_files[diff_item.a_path] = self.repo.git.diff("--cached", diff_item.a_path)
        
        return staged_files

    def generate_commit_message(self, max_tokens: int = 100) -> str:
        """
        Generate a commit message based on staged changes.
        
        Args:
            max_tokens: Maximum number of tokens in the generated message
            
        Returns:
            str: Generated commit message
        """
        staged_changes = self.get_staged_changes()
        
        if not staged_changes:
            return "No staged changes found"

        # Get files being changed to determine scope
        changed_files = list(staged_changes.keys())
        primary_scope = self._determine_scope(changed_files)
        
        # Prepare a concise diff summary
        changes_text = self._prepare_diff_summary(staged_changes)

        # Calculate target length intelligently based on complexity of changes
        target_words = min(max_tokens // 4, 20)  # Cap at 20 words for readability
        
        prompt = f"""Generate a git commit message for these changes:
{changes_text}

Requirements (MUST follow ALL):
1. Format: <type>({primary_scope}): <description>
   - Type: feat|fix|docs|style|refactor|perf|test|build|ci|chore
   - Description: present tense, not capitalized, no period
2. Keep under {target_words} words and {max_tokens} tokens
3. Be specific but concise about WHAT changed
4. Use imperative mood ("add" not "adds")
5. If breaking change, prefix with "BREAKING CHANGE:"

Generate a commit message following ALL the above rules."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            return f"Error generating commit message: {str(e)}"

