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

    def generate_commit_message(self, max_tokens: int = 800) -> str:
        """
        Generate a meaningful git commit message based on staged changes.
        
        Args:
            max_tokens: Maximum number of tokens in the generated message.
                       Default is 800 to ensure full commit messages aren't truncated.
                       Gemini models typically support up to 2048 tokens output.
            
        Returns:
            str: Generated commit message with title and detailed explanation
        """
        staged_changes = self.get_staged_changes()
        
        if not staged_changes:
            return "No staged changes found"
            
        # Ensure reasonable token limit
        if max_tokens < 200:
            max_tokens = 200  # Minimum to ensure complete messages
        elif max_tokens > 2048:
            max_tokens = 2048  # Maximum supported by Gemini

        # Get files being changed
        changed_files = list(staged_changes.keys())
        
        # Prepare a concise diff summary
        changes_text = self._prepare_diff_summary(staged_changes)
        
        # Calculate approximate word limits based on tokens
        approx_words = max_tokens // 4  # rough estimate of 4 tokens per word
        body_words = approx_words - 10   # reserve ~10 words for title
        
        prompt = f"""Analyze these changes and generate a detailed git commit message:
{changes_text}

Requirements for the commit message (STRICT LENGTH LIMITS):
1. Title line:
   - Between 50-72 characters
   - Clear summary of WHAT changed
   - No period at end
2. Leave one blank line after the title
3. Body (approximately {body_words} words total):
   - 2-4 paragraphs explaining:
     * WHY these changes were needed
     * HOW the changes address the need
     * Any important technical details or trade-offs
   - Keep each paragraph under 4 lines
   - Wrap text at 72 characters per line
4. If needed, end with any of these (within {body_words} word limit):
   - Breaking changes
   - Related issues
   - Migration notes
   - Credit to contributors

Example format:
Title summarizing the change

Explain why this change was needed and what problem it solves.
Provide context about the approach taken and any important
implementation details that future maintainers should know.

Include any breaking changes, migration notes, or related
issues at the end as trailers.

Generate a commit message following ALL the above rules. 
Do NOT include any quotes around the commit message."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                    top_p=0.8,  # More focused output
                    top_k=40    # Better vocabulary diversity
                )
            )
            
            message = response.text.strip()
            
            # Ensure proper formatting with line breaks
            parts = message.split('\n\n', 1)
            if len(parts) == 1:
                # Request wasn't properly formatted, try again with more explicit formatting
                response = self.model.generate_content(
                    prompt + "\n\nMake sure to include both a title AND explanatory body!",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.7,
                        top_p=0.8,
                        top_k=40
                    )
                )
                message = response.text.strip()
                parts = message.split('\n\n', 1)
                
            # If we still don't have a proper message, use what we got
            if len(parts) == 1:
                return parts[0]
                
            title, body = parts
            
            # Validate title length (50-72 chars is git standard)
            title = title.strip()
            if len(title) > 72:
                title = title[:69] + "..."
                
            # Format body with proper line wrapping (72-char git standard)
            wrapped_body = []
            for paragraph in body.strip().split('\n\n'):
                lines = []
                current_line = []
                current_length = 0
                
                for word in paragraph.split():
                    if current_length + len(word) + 1 <= 72:
                        current_line.append(word)
                        current_length += len(word) + 1
                    else:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = len(word)
                
                if current_line:
                    lines.append(' '.join(current_line))
                wrapped_body.append('\n'.join(lines))
            
            # Combine all parts with proper formatting
            formatted_message = f"{title}\n\n{'\n\n'.join(wrapped_body)}"
            return formatted_message
            
        except Exception as e:
            return f"Error generating commit message: {str(e)}"

