# 🤖 DiffWhisperer

> Your AI-powered Git companion for crafting perfect commit messages

DiffWhisperer is a powerful CLI tool that uses Google's Gemini AI to automatically generate meaningful, conventional commit messages by analyzing your code changes. Say goodbye to vague commit messages and hello to consistent, professional git history!

## ✨ Why DiffWhisperer?

- 🎯 **Consistent Quality**: Follows conventional commits format for clear, structured history
- 🧠 **Smart Analysis**: Intelligently analyzes code changes to understand context
- 🚀 **Lightning Fast**: Powered by Google's latest Gemini models for quick responses
- 💰 **Cost Effective**: Uses Google's free Gemini AI API
- 🛠️ **Flexible**: Works with any git repository and supports customization
- 🔄 **Seamless Integration**: Easy to add to your existing git workflow

## 🚀 Quick Start

### Installation

```bash
pip install diffwhisperer
```

### Setup

1. Get your free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

2. Set your API key:
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

### Basic Usage

```bash
# Stage your changes
git add .

# Generate a commit message
diffwhisperer generate

# Or generate and commit in one go
diffwhisperer commit
```

## 🎯 Features

### Smart Commit Message Generation

- Automatically detects the type of changes (feat, fix, docs, etc.)
- Identifies the scope based on changed files
- Generates clear, concise descriptions
- Follows the Conventional Commits specification

### Flexible Configuration

```bash
# Choose your preferred Gemini model
diffwhisperer generate --model gemini-2.0-flash

# Customize token length for longer messages
diffwhisperer commit --max-tokens 150

# Work with specific repositories
diffwhisperer generate --repo-path /path/to/repo
```

### Multiple Models Support

- `gemini-2.0-flash`: Quick, efficient responses (default)
- `gemini-2.5-pro`: More detailed analysis
- Any other Gemini supported model!

## 📝 Example Outputs

```bash
# Feature addition
feat(auth): add google oauth integration

# Bug fix
fix(api): resolve race condition in async requests

# Documentation
docs(readme): update installation instructions and examples
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (use DiffWhisperer itself! 😉)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

MIT - Feel free to use this tool in your projects!

---

Made with ❤️ by the DiffWhisperer team

[![PyPI version](https://badge.fury.io/py/diffwhisperer.svg)](https://badge.fury.io/py/diffwhisperer)
[![Build Status](https://github.com/MeherBhaskar/diffwhisperer/actions/workflows/publish.yml/badge.svg)](https://github.com/MeherBhaskar/diffwhisperer/actions/workflows/publish.yml)
