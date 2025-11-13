# Selenium Selector Fixer

Automatically fix broken Selenium XPath selectors using working Playwright tests and Claude AI or Ollama.

## Overview

This tool uses Claude AI or Ollama to intelligently map working Playwright selectors to broken Selenium XPaths and suggests improved, more robust selectors.

## Features

- 🤖 **AI-Powered Analysis**: Uses Claude or Ollama to understand test intent and map selectors
- 🔄 **Automatic Updates**: Updates your Selenium test files with new selectors
- 📊 **Detailed Reports**: Generates comprehensive reports explaining each change
- 🛡️ **Robust Selectors**: Suggests selectors that are less likely to break
- 🎯 **Smart Mapping**: Matches Selenium and Playwright tests based on functionality


### Install and Start Ollama (Recommended for Local AI)

- Download and install Ollama: https://ollama.com/download
- Start the Ollama server:

```bash
ollama serve
```

- Download the required model (e.g. llama3.2):

```bash
ollama pull llama3.2
```

### 4. Make the Script Executable

```bash
chmod +x selector_fixer.py
```

## Usage

```bash
python selector_fixer.py \
  --selenium tests/selenium_test.py \
  --playwright tests/playwright_test.py
```

...existing usage and documentation...