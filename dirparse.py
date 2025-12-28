#!/usr/bin/env python3
"""
dirparse.py - Directory Parser and Consolidator
A GUI tool to parse directory structures and files into a single markdown file.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import datetime
from typing import Set, List, Dict, Optional
import mimetypes

class DirectoryParser:
    """Main application for directory parsing and consolidation."""
    
    # Default excluded extensions (media, documents, binaries, etc.)
    DEFAULT_EXCLUDED_EXTENSIONS = {
        # Media files
        '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.ico',
        '.svg', '.psd', '.ai', '.eps',
        
        # Document files
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt',
        
        # Archive files
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',
        
        # Executable/binary files
        '.exe', '.dll', '.so', '.dylib', '.bin', '.app', '.msi',
        '.iso', '.img', '.dmg',
        
        # System files
        '.db', '.sqlite', '.sqlite3', '.log', '.tmp', '.temp',
        
        # Other
        '.pyc', '.pyo', '__pycache__', '.git', '.gitignore',
    }
    
    # Text file extensions to include (can be read as text)
    TEXT_FILE_EXTENSIONS = {
        '.txt', '.md', '.markdown', '.rst', '.json', '.xml', '.html', '.htm',
        '.css', '.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.c', '.cpp',
        '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
        '.sql', '.sh', '.bash', '.zsh', '.ps1', '.bat', '.yml', '.yaml',
        '.toml', '.ini', '.cfg', '.conf', '.csv', '.tsv', '.tex', '.bib',
        '.asm', '.s', '.v', '.vhdl', '.m', '.mm', '.f', '.for', '.f90',
        '.r', '.lua', '.pl', '.pm', '.tcl', '.vbs', '.asp', '.aspx',
        '.jsp', '.scala', '.dart', '.elm', '.clj', '.cljs', '.erl', '.hrl',
        '.ex', '.exs', '.fs', '.fsx', '.fsi', '.ml', '.mli', '.hs', '.lhs',
        '.purs', '.coffee', '.litcoffee', '.ass', '.vue', '.svelte', '.elm',
    }
    
    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("Directory Parser - Consolidate to Markdown")
        self.root.geometry("900x700")
        
        # Set application icon if available
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        # Variables
        self.selected_directory = tk.StringVar()
        self.output_filename = tk.StringVar(value="directory_consolidated.md")
        self.excluded_extensions = set(self.DEFAULT_EXCLUDED_EXTENSIONS)
        self.custom_exclusions = set()
        self.include_hidden = tk.BooleanVar(value=False)
        self.include_empty_dirs = tk.BooleanVar(value=False)
        self.max_file_size = tk.IntVar(value=10)  # MB
        
        # Store for treeview items
        self.tree_items = {}
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI components."""
        # Create main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        
        # Row 0: Title
        title_label = ttk.Label(
            main_container,
            text="📁 Directory Parser & Consolidator",
            font=('Helvetica', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Row 1: Directory Selection
        ttk.Label(main_container, text="Directory:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 5)
        )
        
        dir_entry = ttk.Entry(
            main_container,
            textvariable=self.selected_directory,
            width=50
        )
        dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(
            main_container,
            text="Browse...",
            command=self.browse_directory
        )
        browse_btn.grid(row=1, column=2, sticky=tk.W)
        
        # Row 2: Output Filename
        ttk.Label(main_container, text="Output File:").grid(
            row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0)
        )
        
        output_entry = ttk.Entry(
            main_container,
            textvariable=self.output_filename,
            width=50
        )
        output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), 
                         padx=(0, 5), pady=(10, 0))
        
        # Row 3: Options Frame
        options_frame = ttk.LabelFrame(main_container, text="Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, 
                          sticky=(tk.W, tk.E), pady=(15, 10))
        options_frame.columnconfigure(0, weight=1)
        
        # Options checkboxes
        ttk.Checkbutton(
            options_frame,
            text="Include hidden files/folders",
            variable=self.include_hidden
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        ttk.Checkbutton(
            options_frame,
            text="Include empty directories",
            variable=self.include_empty_dirs
        ).grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        # File size limit
        size_frame = ttk.Frame(options_frame)
        size_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        ttk.Label(size_frame, text="Max file size (MB):").pack(side=tk.LEFT, padx=(0, 5))
        size_spinbox = ttk.Spinbox(
            size_frame,
            from_=1,
            to=100,
            textvariable=self.max_file_size,
            width=10
        )
        size_spinbox.pack(side=tk.LEFT)
        
        # Row 4: Exclusions Frame
        exclusions_frame = ttk.LabelFrame(
            main_container, 
            text="Excluded Extensions/Directories",
            padding="10"
        )
        exclusions_frame.grid(row=4, column=0, columnspan=3, 
                            sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 10))
        exclusions_frame.columnconfigure(0, weight=1)
        exclusions_frame.rowconfigure(0, weight=1)
        
        # Treeview for exclusions
        columns = ('type', 'item')
        self.exclusions_tree = ttk.Treeview(
            exclusions_frame,
            columns=columns,
            show='headings',
            height=8
        )
        
        # Define headings
        self.exclusions_tree.heading('type', text='Type')
        self.exclusions_tree.heading('item', text='Extension/Directory')
        
        # Define columns
        self.exclusions_tree.column('type', width=100, anchor=tk.W)
        self.exclusions_tree.column('item', width=300, anchor=tk.W)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            exclusions_frame,
            orient=tk.VERTICAL,
            command=self.exclusions_tree.yview
        )
        self.exclusions_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid treeview and scrollbar
        self.exclusions_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Buttons for exclusions
        btn_frame = ttk.Frame(exclusions_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(
            btn_frame,
            text="Add Extension",
            command=self.add_extension
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            btn_frame,
            text="Add Directory Pattern",
            command=self.add_directory_pattern
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Remove Selected",
            command=self.remove_exclusion
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Reset to Defaults",
            command=self.reset_exclusions
        ).pack(side=tk.LEFT, padx=5)
        
        # Row 5: Status and Progress
        status_frame = ttk.Frame(main_container)
        status_frame.grid(row=5, column=0, columnspan=3, 
                         sticky=(tk.W, tk.E), pady=(10, 5))
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            foreground="green"
        )
        self.status_label.pack(side=tk.LEFT, anchor=tk.W)
        
        self.progress = ttk.Progressbar(
            main_container,
            mode='indeterminate',
            length=400
        )
        self.progress.grid(row=6, column=0, columnspan=3, 
                          sticky=(tk.W, tk.E), pady=(5, 10))
        
        # Row 7: Action Buttons
        action_frame = ttk.Frame(main_container)
        action_frame.grid(row=7, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(
            action_frame,
            text="📊 Preview Directory",
            command=self.preview_directory,
            width=20
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            action_frame,
            text="🔄 Parse & Consolidate",
            command=self.start_parsing,
            width=20
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            action_frame,
            text="❌ Exit",
            command=self.root.quit,
            width=20
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Row 8: Log/Console
        log_frame = ttk.LabelFrame(main_container, text="Console Output", padding="10")
        log_frame.grid(row=8, column=0, columnspan=3, 
                      sticky=(tk.W, tk.E, tk.N, tk.S), pady=(15, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.console = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            wrap=tk.WORD,
            font=('Courier', 9)
        )
        self.console.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure weights for resizing
        main_container.rowconfigure(8, weight=1)
        
        # Load default exclusions
        self.load_default_exclusions()
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages to the console."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        tag_colors = {
            "INFO": "black",
            "SUCCESS": "green",
            "WARNING": "orange",
            "ERROR": "red",
            "DEBUG": "blue"
        }
        
        color = tag_colors.get(level, "black")
        formatted_msg = f"[{timestamp}] {message}\n"
        
        self.console.insert(tk.END, formatted_msg)
        self.console.tag_config(level, foreground=color)
        self.console.see(tk.END)
        self.root.update_idletasks()
        
    def browse_directory(self):
        """Open directory browser dialog."""
        directory = filedialog.askdirectory(title="Select Directory to Parse")
        if directory:
            self.selected_directory.set(directory)
            self.log(f"Selected directory: {directory}")
            
    def add_extension(self):
        """Add a custom extension to exclude."""
        extension = tk.simpledialog.askstring(
            "Add Extension",
            "Enter extension to exclude (e.g., .tmp, .log):",
            parent=self.root
        )
        
        if extension:
            if not extension.startswith('.'):
                extension = '.' + extension
            
            if extension not in self.custom_exclusions:
                self.custom_exclusions.add(extension)
                self.exclusions_tree.insert(
                    '', 'end', 
                    values=('Extension', extension)
                )
                self.log(f"Added extension to exclude: {extension}")
                
    def add_directory_pattern(self):
        """Add a directory pattern to exclude."""
        pattern = tk.simpledialog.askstring(
            "Add Directory Pattern",
            "Enter directory name/pattern to exclude (e.g., node_modules, __pycache__):",
            parent=self.root
        )
        
        if pattern:
            if pattern not in self.custom_exclusions:
                self.custom_exclusions.add(pattern)
                self.exclusions_tree.insert(
                    '', 'end', 
                    values=('Directory', pattern)
                )
                self.log(f"Added directory pattern to exclude: {pattern}")
                
    def remove_exclusion(self):
        """Remove selected exclusion."""
        selected = self.exclusions_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to remove.")
            return
            
        for item in selected:
            values = self.exclusions_tree.item(item, 'values')
            if values:
                exclusion = values[1]
                self.custom_exclusions.discard(exclusion)
                self.exclusions_tree.delete(item)
                self.log(f"Removed exclusion: {exclusion}")
                
    def reset_exclusions(self):
        """Reset exclusions to default."""
        if messagebox.askyesno("Reset Exclusions", 
                              "Reset all custom exclusions to defaults?"):
            self.custom_exclusions.clear()
            self.load_default_exclusions()
            self.log("Reset exclusions to defaults")
            
    def load_default_exclusions(self):
        """Load default exclusions into treeview."""
        # Clear treeview
        for item in self.exclusions_tree.get_children():
            self.exclusions_tree.delete(item)
            
        # Add default extensions
        for ext in sorted(self.DEFAULT_EXCLUDED_EXTENSIONS):
            self.exclusions_tree.insert(
                '', 'end',
                values=('Extension', ext)
            )
            
    def is_excluded(self, path: Path) -> bool:
        """Check if a path should be excluded."""
        # Check if it's a hidden file/directory (starts with .)
        if not self.include_hidden.get():
            if path.name.startswith('.'):
                return True
                
        # Check if it's a directory pattern
        for exclusion in self.custom_exclusions:
            if exclusion in str(path):
                if not exclusion.startswith('.'):  # Directory pattern
                    return True
                    
        # Check file extensions
        if path.is_file():
            # Combine default and custom exclusions
            all_exclusions = self.DEFAULT_EXCLUDED_EXTENSIONS.union(self.custom_exclusions)
            
            # Check extension
            suffix = path.suffix.lower()
            if suffix in all_exclusions:
                return True
                
            # Check file size
            max_bytes = self.max_file_size.get() * 1024 * 1024
            try:
                if path.stat().st_size > max_bytes:
                    return True
            except:
                pass
                
        return False
        
    def preview_directory(self):
        """Preview directory structure without parsing."""
        directory = self.selected_directory.get()
        if not directory or not os.path.exists(directory):
            messagebox.showerror("Error", "Please select a valid directory.")
            return
            
        self.log("Starting directory preview...", "INFO")
        self.status_label.config(text="Previewing...", foreground="blue")
        
        # Run in thread to avoid GUI freeze
        thread = threading.Thread(target=self._do_preview, daemon=True)
        thread.start()
        
    def _do_preview(self):
        """Preview directory structure."""
        directory = Path(self.selected_directory.get())
        
        try:
            file_count = 0
            dir_count = 0
            total_size = 0
            
            for root, dirs, files in os.walk(directory):
                root_path = Path(root)
                
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not self.is_excluded(root_path / d)]
                
                dir_count += 1
                
                for file in files:
                    file_path = root_path / file
                    if not self.is_excluded(file_path):
                        file_count += 1
                        try:
                            total_size += file_path.stat().st_size
                        except:
                            pass
                            
            # Display summary
            self.log(f"Directory: {directory}", "INFO")
            self.log(f"Total directories: {dir_count}", "INFO")
            self.log(f"Total files to parse: {file_count}", "INFO")
            self.log(f"Estimated size: {total_size / (1024*1024):.2f} MB", "INFO")
            self.log("Preview completed.", "SUCCESS")
            self.status_label.config(text="Preview completed", foreground="green")
            
        except Exception as e:
            self.log(f"Error during preview: {str(e)}", "ERROR")
            self.status_label.config(text="Preview failed", foreground="red")
            
    def start_parsing(self):
        """Start the parsing and consolidation process."""
        directory = self.selected_directory.get()
        if not directory or not os.path.exists(directory):
            messagebox.showerror("Error", "Please select a valid directory.")
            return
            
        output_file = self.output_filename.get()
        if not output_file.endswith('.md'):
            output_file += '.md'
            self.output_filename.set(output_file)
            
        self.log("Starting parsing process...", "INFO")
        self.status_label.config(text="Parsing...", foreground="blue")
        self.progress.start()
        
        # Disable buttons during processing
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.config(state=tk.DISABLED)
                
        # Run in thread to avoid GUI freeze
        thread = threading.Thread(target=self._do_parsing, daemon=True)
        thread.start()
        
    def _do_parsing(self):
        """Perform the actual parsing."""
        directory = Path(self.selected_directory.get())
        output_file = Path(self.output_filename.get())
        
        try:
            with open(output_file, 'w', encoding='utf-8') as md_file:
                # Write header
                md_file.write(f"# Directory Consolidation Report\n\n")
                md_file.write(f"**Directory:** `{directory}`\n\n")
                md_file.write(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                md_file.write(f"**Excluded extensions/patterns:**\n")
                
                # List exclusions
                all_exclusions = list(self.DEFAULT_EXCLUDED_EXTENSIONS) + list(self.custom_exclusions)
                for excl in sorted(all_exclusions)[:20]:  # Show first 20
                    md_file.write(f"- `{excl}`\n")
                if len(all_exclusions) > 20:
                    md_file.write(f"- ... and {len(all_exclusions) - 20} more\n")
                md_file.write("\n" + "="*50 + "\n\n")
                
                # Walk through directory
                file_count = 0
                dir_count = 0
                skipped_count = 0
                
                for root, dirs, files in os.walk(directory):
                    root_path = Path(root)
                    rel_path = root_path.relative_to(directory)
                    
                    # Skip excluded directories
                    dirs[:] = [d for d in dirs if not self.is_excluded(root_path / d)]
                    
                    # Write directory header
                    if str(rel_path) != '.' or self.include_empty_dirs.get():
                        dir_count += 1
                        depth = len(rel_path.parts)
                        indent = "#" * min(depth + 1, 6)
                        md_file.write(f"\n{indent} Directory: `{rel_path}`\n\n")
                        
                        # List subdirectories
                        if dirs and self.include_empty_dirs.get():
                            md_file.write("**Subdirectories:**\n")
                            for d in sorted(dirs):
                                md_file.write(f"- `{d}`\n")
                            md_file.write("\n")
                    
                    # Process files
                    for file in sorted(files):
                        file_path = root_path / file
                        
                        if self.is_excluded(file_path):
                            skipped_count += 1
                            continue
                            
                        file_count += 1
                        self.log(f"Processing: {file_path.name}", "DEBUG")
                        
                        # Write file header
                        md_file.write(f"\n### File: `{file}`\n\n")
                        md_file.write(f"**Path:** `{rel_path}/{file}`\n")
                        md_file.write(f"**Extension:** `{file_path.suffix}`\n")
                        
                        try:
                            file_size = file_path.stat().st_size
                            md_file.write(f"**Size:** {file_size:,} bytes ({file_size/1024:.2f} KB)\n\n")
                        except:
                            md_file.write(f"**Size:** Unknown\n\n")
                        
                        # Try to read and include file content
                        try:
                            # Check if it's a text file
                            suffix = file_path.suffix.lower()
                            if suffix in self.TEXT_FILE_EXTENSIONS:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    
                                # Escape markdown special characters if needed
                                if suffix in {'.md', '.markdown'}:
                                    md_file.write("**Content:**\n\n")
                                    md_file.write(content)
                                else:
                                    md_file.write("```" + suffix[1:] + "\n")
                                    md_file.write(content)
                                    if not content.endswith('\n'):
                                        md_file.write("\n")
                                    md_file.write("```\n")
                            else:
                                # For non-text files, just note the type
                                mime_type, _ = mimetypes.guess_type(str(file_path))
                                md_file.write(f"*Binary file - {mime_type or 'Unknown type'}*\n")
                                
                        except UnicodeDecodeError:
                            md_file.write("*[Content skipped - binary or unsupported encoding]*\n")
                        except Exception as e:
                            md_file.write(f"*[Error reading file: {str(e)}]*\n")
                            
                        md_file.write("\n" + "-"*40 + "\n")
                        
            # Update UI with completion
            self.log(f"\nParsing completed successfully!", "SUCCESS")
            self.log(f"Output saved to: {output_file.absolute()}", "SUCCESS")
            self.log(f"Directories processed: {dir_count}", "INFO")
            self.log(f"Files processed: {file_count}", "INFO")
            self.log(f"Files skipped: {skipped_count}", "INFO")
            
            self.status_label.config(text="Parsing completed!", foreground="green")
            self.progress.stop()
            
            # Re-enable buttons
            self.root.after(0, self._enable_buttons)
            
            # Ask to open the file
            if messagebox.askyesno("Success", 
                                  f"Successfully parsed {file_count} files.\n"
                                  f"Open the generated markdown file?"):
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(output_file.absolute())
                    elif os.name == 'posix':  # macOS, Linux
                        import subprocess
                        subprocess.run(['xdg-open', str(output_file.absolute())])
                except:
                    pass
                    
        except Exception as e:
            self.log(f"Error during parsing: {str(e)}", "ERROR")
            self.status_label.config(text="Parsing failed", foreground="red")
            self.progress.stop()
            self.root.after(0, self._enable_buttons)
            
    def _enable_buttons(self):
        """Re-enable all buttons after processing."""
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.config(state=tk.NORMAL)

def main():
    """Main entry point."""
    root = tk.Tk()
    app = DirectoryParser(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()