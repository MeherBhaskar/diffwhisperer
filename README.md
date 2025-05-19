# DiffWhisperer

An AI agent for generating meaningful git commit messages using Google's Gemini AI.

## Installation

```bash
pip install diffwhisperer
```

## Usage

1. Get a Google API key from https://makersuite.google.com/app/apikey

2. Set your API key:
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

3. Use DiffWhisperer to generate commit messages:
```bash
# Stage your changes first
git add .

# Just generate a commit message
diffwhisperer generate

# Generate and commit in one go
diffwhisperer commit

# Customize the model
diffwhisperer generate --model gemini-1.5-pro

# Or use other options
diffwhisperer commit --repo-path /path/to/repo --max-tokens 150
```

## Features

- Uses Google's free Gemini AI API (with model selection)
- Generates commit messages following conventional commits format
- Can automatically commit changes with the generated message
- Analyzes staged changes in git repositories
- Smart scope detection based on changed files
- Easy to integrate into your git workflow
- Supports multiple Gemini models (e.g., gemini-2.0-flash, gemini-1.5-pro)

## Example Output

```
feat(auth): add google oauth integration
```

## License

MIT
