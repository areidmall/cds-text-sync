# Contributing to cds-text-sync

First off, thank you for considering contributing to `cds-text-sync`! It's people like you who make it a great tool for the CODESYS community.

## 🚀 How Can I Contribute?

### Reporting Bugs
If you find a bug, please open an issue! Be as specific as possible:
* What version of CODESYS are you using?
* What script were you running?
* What was the error message (if any)?
* Can you provide a small code snippet or export that reproduces the issue?

### Suggesting Enhancements
We are always looking for ways to improve the workflow. If you have an idea:
* Open an issue with the "Enhancement" tag.
* Explain the use case and why it would be beneficial.

### Pull Requests
1. **Fork the repo** and create your branch from `main`.
2. **If you've added code**, make sure it follows the existing style (clean, documented).
3. **Test your changes** in a dummy CODESYS project before submitting.
4. **Update the README** if you've added new features or changed workflows.
5. **Issue a Pull Request** with a clear description of what you've changed.

## 🛠️ Development Setup

Since these are CODESYS Python scripts, testing requires:
1. **CODESYS IDE** installed.
2. The **CODESYS Script Engine** enabled.
3. Placing the scripts in the `ScriptDir` as described in the README.

### Code Style
* Use clear variable names.
* Keep the `Project_` prefix for main execution scripts so they group together in the CODESYS menu.
* Preserve the "Marker" logic (`// ---`, `// === IMPLEMENTATION ===`) as many users rely on these for LLM processing.

## ⚖️ License
By contributing, you agree that your contributions will be licensed under its **MIT License**.
