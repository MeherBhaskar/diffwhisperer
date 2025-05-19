"""
Command-line interface for DiffWhisperer
"""

import click
from pathlib import Path
import os
from git import Repo
from .analyzer import DiffAnalyzer


@click.group()
def cli():
    """DiffWhisperer - AI-powered git commit message generator"""
    pass

@cli.command()
@click.option(
    "--repo-path",
    "-p",
    default=".",
    help="Path to the git repository (defaults to current directory)",
)
@click.option(
    "--api-key",
    "-k",
    envvar="GOOGLE_API_KEY",
    help="Google API key (can also be set via GOOGLE_API_KEY environment variable)",
)
@click.option(
    "--model",
    "-m",
    default="gemini-2.0-flash",
    help="Gemini model to use (e.g., gemini-2.0-flash, gemini-1.5-pro)",
)
@click.option(
    "--max-tokens",
    "-t",
    default=100,
    help="Maximum number of tokens in the generated message",
)
def generate(repo_path: str, api_key: str, model: str, max_tokens: int):
    """Generate an AI-powered commit message based on your staged changes."""
    try:
        analyzer = DiffAnalyzer(repo_path=repo_path, api_key=api_key, model_name=model)
        message = analyzer.generate_commit_message(max_tokens=max_tokens)
        click.echo(message)
        return message
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)

@cli.command()
@click.option(
    "--repo-path",
    "-p",
    default=".",
    help="Path to the git repository (defaults to current directory)",
)
@click.option(
    "--api-key",
    "-k",
    envvar="GOOGLE_API_KEY",
    help="Google API key (can also be set via GOOGLE_API_KEY environment variable)",
)
@click.option(
    "--model",
    "-m",
    default="gemini-2.0-flash",
    help="Gemini model to use (e.g., gemini-2.0-flash, gemini-1.5-pro)",
)
@click.option(
    "--max-tokens",
    "-t",
    default=100,
    help="Maximum number of tokens in the generated message",
)
def commit(repo_path: str, api_key: str, model: str, max_tokens: int):
    """Generate a commit message and automatically commit staged changes."""
    try:
        analyzer = DiffAnalyzer(repo_path=repo_path, api_key=api_key, model_name=model)
        message = analyzer.generate_commit_message(max_tokens=max_tokens)
        if message == "No staged changes found":
            click.echo(message)
            exit(1)
        repo = Repo(repo_path)
        repo.index.commit(message)
        click.echo(f"✓ Committed with message: {message}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)

if __name__ == "__main__":
    cli()

