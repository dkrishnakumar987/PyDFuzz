# PyDFuzz

An open-source fuzzing utility for MuPDF in Python.

> **DISCLAIMER:** This project is a work in progress. Some features may be incomplete or subject to change.

## Overview

PyDFuzz is a specialized tool designed to generate corrupted PDF files that can be used to test the robustness of MuPDF and identify security vulnerabilities through fuzzing techniques. It works on both Windows and Linux operating systems.

The project focuses on different corruption strategies to thoroughly test PDF parsers:
- Font definition corruption
- JavaScript injection
- Content stream corruption 
- Cross-reference (xref) table corruption
- Deep Fuzzing using AFL++ or WinAFL

## Features

- 📄 Generate randomized PDF files
- 🧪 Multiple PDF corruption techniques
- 🔨 Command-line interface for easy integration
- 📊 Detailed logging
- 🚀 Easy to extend with new corruption techniques
- 🔬 AFL++/WinAFL integration for deep fuzzing (WIP)
- 💾 Crash state save functionality (WIP)
- 🔍 Memory debugging with gdb/WinDbg (WIP)
- 🖥️ TUI Interface for easier fuzzing management (WIP)

## Installation

### Prerequisites

Before installing PyDFuzz, make sure you have:
- Python 3.12 or newer
- Poetry (dependency management tool)

For detailed installation instructions, see our Prerequisites Guide.

### Installing PyDFuzz

```bash
# Install from source
git clone https://github.com/dkrishnakumar987/PyDFuzz.git
cd PyDFuzz
poetry install
poetry shell
```

## Quick Start

Generate a corrupted PDF with random corruption:

```bash
pydfuzz-cli --generator random
```

Generate a PDF with specific corruption:

```bash
# Font corruption
pydfuzz-cli --generator font

# JavaScript injection
pydfuzz-cli --generator javascript

# Stream corruption
pydfuzz-cli --generator stream

# XREF table corruption
pydfuzz-cli --generator xref
```

## How It Works

PyDFuzz uses a modular architecture with different PDF generators:

1. `BasePDFGenerator` - Abstract base class for generating PDF files
2. `CorruptFontPDFGenerator` - Replaces valid font names with random invalid strings
3. `CorruptJavaScriptPDFGenerator` - Injects malicious JavaScript
4. `CorruptStreamPDFGenerator` - Corrupts content streams with enormous data
5. `CorruptXrefPDFGenerator` - Corrupts cross-reference tables

The `fuzzing_manager` orchestrates the fuzzing process, and the `cli` provides a command line interface.

## Project Structure

```
pydfuzz/
├── src/
│   ├── pydfuzz/
│   │   ├── cli.py                 # Command-line interface
│   │   ├── fuzzing_manager.py     # Core fuzzing orchestration
│   │   ├── logger.py              # Logging configuration
│   │   └── pdf_generator/         # PDF generation modules
├── tests/                         # Test suite
└── docs/                          # Documentation
```

## Documentation

For more detailed documentation, please explore:

- [Contribution Guidelines](./docs/contribute.md) - How to contribute to PyDFuzz
- [Prerequisites Guide](./docs/prerequisite.md) - Installation requirements

## Contributing

We welcome contributions! To get started:

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Submit a pull request

Please see our [Contribution Guidelines](./docs/contribute.md) for detailed instructions.

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Acknowledgements

- [pdfrw](https://github.com/pmaupin/pdfrw) library for PDF manipulation
- [MuPDF](https://mupdf.com/) PDF rendering engine

---

📝 PyDFuzz is a research tool designed for security testing only. Do not use generated PDFs with production PDF readers unless you fully understand the risks.