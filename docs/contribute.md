# Contributing to PyDFuzz

This guide explains how to fork, clone, and contribute to PyDFuzz for development purposes.

[← Back to README](../README.md)

## Fork and Clone the Repository

To contribute to PyDFuzz, you'll first need to fork the repository and then clone your fork:

1. **Fork the repository**:
   - Visit the [PyDFuzz GitHub repository](https://github.com/dkrishnakumar987/PyDFuzz)
   - Click the "Fork" button in the upper-right corner
   - This creates a copy of the repository in your GitHub account

2. **Clone your fork**:
   ```bash
   # Clone your fork to your local machine
   git clone https://github.com/YOUR-USERNAME/PyDFuzz.git
   cd PyDFuzz
   ```

3. **Add the upstream remote**:
   ```bash
   # Add the original repository as "upstream" remote
   git remote add upstream https://github.com/dkrishnakumar987/PyDFuzz.git
   ```

## Prerequisites

Before building PyDFuzz, ensure you have the necessary prerequisites installed:

- Python 3.12 or newer
- Poetry (dependency management tool)

For detailed instructions on installing these prerequisites, see the [prerequisites guide](./prerequisite.md).

## Setting Up the Development Environment

### 1. Install Dependencies

Once you've cloned your fork and installed Poetry, you can install all project dependencies:

```bash
# Install all dependencies including development dependencies
poetry install
```

This command creates a virtual environment and installs all required dependencies specified in the `pyproject.toml` file.

### 2. Activate the Virtual Environment

To activate the Poetry-created virtual environment:

```bash
# Activate the virtual environment
poetry shell
```

## Project Structure

The project is organized as follows:

- `src/pydfuzz` - Main source code
  - `pdf_generator/` - PDF generation and corruption modules
  - `logger.py` - Logging configuration
  - `fuzzing_manager.py` - Core fuzzing functionality
  - `cli.py` - Command-line interface
- `tests` - Test suite
- `docs` - Documentation

## Development Workflow

1. **Keep your fork updated**:
   ```bash
   # Fetch changes from upstream
   git fetch upstream
   
   # Merge changes from upstream/main into your local main branch
   git checkout main
   git merge upstream/main
   
   # Push the updates to your fork
   git push origin main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**:
   - Implement your feature or fix
   - Add appropriate tests in the `tests` directory

4. **Run tests**:
   ```bash
   poetry run runtests
   ```

5. **Commit your changes**:
   PyDFuzz uses conventional commits:
   ```bash
   git commit -m "feat: add your feature description"
   ```
   
   Common commit types:
   - `feat`: New feature
   - `fix`: Bug fix
   - docs: Documentation changes
   - `test`: Adding or updating tests
   - `refactor`: Code changes that neither fix bugs nor add features

6. **Push your changes to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a pull request**:
   - Go to your fork on GitHub
   - Click "Pull Request" and then "New Pull Request"
   - Select your feature branch and submit the pull request with a clear description of your changes

## Pre-commit Hooks

PyDFuzz uses pre-commit hooks to ensure code quality. To set them up:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install
```

This will ensure your commits follow the conventional commit format.

## Directory Structure for Generated Files

When running PyDFuzz, it creates several directories:

- `generated_pdfs` - Contains the generated corrupted PDF files
- `input_pdfs` - Directory for input PDF files (optional)
- `log` - Contains log files

---

[← Back to README](../README.md)