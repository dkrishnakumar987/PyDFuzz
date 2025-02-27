# Prerequisites for PyDFuzz

Before you start working with PyDFuzz, you need to ensure your system has the required software installed. This guide will help you install Python and Poetry, which are essential prerequisites for running PyDFuzz.

[← Back to README](../README.md)

## Python Installation

PyDFuzz requires Python 3.12 or newer.

### Windows

1. **Download Python**:
   - Visit the official [Python Downloads page](https://www.python.org/downloads/).
   - Click on the "Download Python 3.12.x" button (or newer version).
   - Make sure to check "Add Python to PATH" during installation.

2. **Run the installer**:
   - Follow the installation wizard.
   - Select "Customize installation" if you want to change the installation location.
   - Click "Install Now" to start the installation process.

3. **Verify installation**:
   - Open Command Prompt (cmd) and type:
     ```
     python --version
     ```
   - You should see the Python version displayed.

### Linux

#### Ubuntu/Debian

1. **Update package list**:
   ```bash
   sudo apt update
   ```

2. **Install required packages**:
   ```bash
   sudo apt install -y software-properties-common
   ```

3. **Add the deadsnakes PPA** (to get Python 3.12):
   ```bash
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt update
   ```

4. **Install Python 3.12**:
   ```bash
   sudo apt install -y python3.12 python3.12-venv python3.12-dev
   ```

5. **Verify installation**:
   ```bash
   python3.12 --version
   ```

#### Fedora

1. **Install Python 3.12**:
   ```bash
   sudo dnf install python3.12
   ```

2. **Verify installation**:
   ```bash
   python3.12 --version
   ```

#### Arch Linux

1. **Install Python**:
   ```bash
   sudo pacman -S python
   ```

2. **Verify installation**:
   ```bash
   python --version
   ```
## Poetry Installation

Poetry is a dependency management and packaging tool in Python. We recommend installing Poetry using pipx, which is a tool to install and run Python applications in isolated environments.

### Install pipx first

#### Windows

1. **Install pipx**:
   ```powershell
   python -m pip install --user pipx
   python -m pipx ensurepath
   ```

2. **Verify pipx installation**:
   ```powershell
   pipx --version
   ```

#### Linux/macOS

1. **Install pipx**:
   ```bash
   python3 -m pip install --user pipx
   python3 -m pipx ensurepath
   ```

2. **Verify pipx installation**:
   ```bash
   pipx --version
   ```

### Install Poetry using pipx

#### Windows

1. **Install Poetry**:
   ```powershell
   pipx install poetry
   ```

2. **Verify installation**:
   ```powershell
   poetry --version
   ```

#### Linux/macOS

1. **Install Poetry**:
   ```bash
   pipx install poetry
   ```

2. **Verify installation**:
   ```bash
   poetry --version
   ```

## Troubleshooting

### Common Issues

1. **Python not found in PATH**:
   - Windows: Reinstall Python and make sure to check "Add Python to PATH"
   - Linux: Make sure you're using the correct Python command (`python3`, `python3.12`)

2. **pipx not found in PATH**:
   - Ensure you've run `python -m pipx ensurepath` and restarted your terminal
   - On Windows, you might need to reopen your terminal or restart your computer

3. **Poetry not found in PATH**:
   - When using pipx, Poetry should be automatically added to your PATH
   - Try running `pipx ensurepath` and restart your terminal

4. **Permission errors on Linux**:
   - Use `--user` flag with pip installations to avoid permission issues
   - Consider using a virtual environment to avoid permission issues

## Additional Resources

- [Python Documentation](https://docs.python.org/)
- [pipx Documentation](https://pypa.github.io/pipx/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Python Virtual Environments Guide](https://docs.python.org/3/library/venv.html)

---

[← Back to README](../README.md)