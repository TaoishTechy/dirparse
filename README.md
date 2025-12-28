# Dirparse - Directory Parser & Consolidator

**A simple Python GUI tool to parse a directory structure and consolidate text-based file contents into a single Markdown file.**

Perfect for code reviews, project documentation, archiving source code, or quickly consolidating text files from a folder (while skipping binaries, media, and large files).

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)](https://docs.python.org/3/library/tkinter.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*gExample screenshots of similar Tkinter-based directory tools*

## Features

- **Graphical User Interface** built with Tkinter (no command-line needed)
- Select any directory and generate a clean **Markdown (.md)** report
- Automatically includes file contents for common text/code files (`.py`, `.js`, `.html`, `.json`, `.txt`, etc.)
- Syntax-highlighted code blocks in the output Markdown
- Skips binary files, media, archives, and large files by default
- Customizable exclusions (extensions or directory patterns like `node_modules`)
- Options for:
  - Including hidden files/folders
  - Including empty directories
  - Setting max file size (in MB)
- Preview mode to estimate files/directories before parsing
- Real-time console log and progress indicator
- One-click open of the generated Markdown file

*Example Markdown document icon*

## Installation

### Requirements
- Python 3.8 or higher
- Tkinter (comes bundled with standard Python installations on most systems)

No additional packages are required!

### Download
1. Clone or download the repository:
   ```bash
   git clone https://github.com/TaoishTechy/Dirparse.git
   cd Dirparse
   ```

2. The main script is `dirparse.py`

## Usage

Run the application:

```bash
python dirparse.py
```

### Steps in the GUI
1. Click **Browse...** to select the target directory.
2. (Optional) Adjust options:
   - Include hidden files
   - Include empty directories
   - Set maximum file size
   - Add/remove excluded extensions or directory patterns (e.g., `.log`, `venv`, `__pycache__`)
3. Click **Preview Directory** to see a summary of what will be processed.
4. Click **Parse & Consolidate** to generate the Markdown file.
5. The output file (default: `directory_consolidated.md`) will be saved in the current working directory.
6. Optionally open the file automatically when complete.

The generated Markdown includes:
- Directory tree structure
- File metadata (path, size, extension)
- Full file contents in fenced code blocks
- Clear separation between files

## Example Output Snippet

```markdown
# Directory Consolidation Report

**Directory:** `/path/to/your/project`

**Generated:** 2025-12-27 14:30:45

## Directory: `src`

### File: `main.py`

**Path:** `src/main.py`
**Extension:** `.py`
**Size:** 1,234 bytes (1.21 KB)

```python
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
```
```

## Contributing

Contributions are welcome! Feel free to:
- Open issues for bugs or feature requests
- Submit pull requests with improvements

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by [TaoishTechy](https://github.com/TaoishTechy)
