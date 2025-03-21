import os
import threading
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

from pydfuzz.crash_handler import CrashHandler
from pydfuzz.debugger import FuzzDebugger
from pydfuzz.fuzz_executor import FuzzExecutor
from pydfuzz.fuzzing_manager import run_fuzzer
from pydfuzz.logger import logger

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class PyDFuzzGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Initialize core components
        self.fuzz_executor = FuzzExecutor()
        self.crash_handler = CrashHandler(self.fuzz_executor.output_crashes_dir)
        self.debugger = FuzzDebugger(
            self.fuzz_executor.xpdf_bin,
            self.fuzz_executor.output_dir,
            self.fuzz_executor.output_crashes_dir,
        )

        # Configure window
        self.title("PyDFuzz")
        self.geometry("800x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Create the tabview
        self.create_tabs()

        # Create status bar
        self.create_status_bar()

        # Initialize state variables
        self._stop_fuzzing_requested = False

    def create_tabs(self):
        """Create the tab view with all function tabs"""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        # Add tabs
        self.tabview.add("Generation")
        self.tabview.add("Fuzzing")
        self.tabview.add("Crashes")
        # Removed "Memory" tab

        # Configure tab content
        self.setup_generation_tab()
        self.setup_fuzzing_tab()
        self.setup_crashes_tab()
        # Removed call to setup_memory_tab()

    def create_status_bar(self):
        """Create the status bar at the bottom"""
        status_frame = ctk.CTkFrame(self, height=30)
        status_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(status_frame, text="Status: Ready")
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Progress indicator
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=200)
        self.progress_bar.grid(row=0, column=1, padx=10, pady=5)
        self.progress_bar.set(0)

        # Theme selector
        appearance_menu = ctk.CTkOptionMenu(
            status_frame,
            values=["System", "Light", "Dark"],
            command=self.change_appearance,
        )
        appearance_menu.grid(row=0, column=2, padx=10, pady=5)

    def setup_generation_tab(self):
        """Setup the PDF generation tab"""
        tab = self.tabview.tab("Generation")
        tab.grid_columnconfigure(0, weight=1)

        # Title label
        title = ctk.CTkLabel(
            tab, text="PDF Generation", font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Main frame for controls
        frame = ctk.CTkFrame(tab)
        frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)

        # Number of samples
        samples_label = ctk.CTkLabel(frame, text="Number of samples:")
        samples_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.samples_entry = ctk.CTkEntry(frame, width=100)
        self.samples_entry.insert(0, "10")
        self.samples_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Corruption type
        generator_label = ctk.CTkLabel(frame, text="Corruption type:")
        generator_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.generator_var = ctk.StringVar(value="random")
        generator_menu = ctk.CTkOptionMenu(
            frame,
            values=["random", "font", "javascript", "stream", "xref"],
            variable=self.generator_var,
        )
        generator_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Generate button
        generate_button = ctk.CTkButton(
            frame,
            text="Generate PDFs",
            fg_color="green",
            hover_color="dark green",
            command=self.generate_pdfs,
        )
        generate_button.grid(row=2, column=0, columnspan=2, padx=20, pady=20)

        # Log area
        log_label = ctk.CTkLabel(tab, text="Generation Log:")
        log_label.grid(row=2, column=0, padx=20, pady=(20, 5), sticky="w")

        self.generation_log = ctk.CTkTextbox(tab, height=200)
        self.generation_log.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")

    def setup_fuzzing_tab(self):
        """Setup the PDF fuzzing tab"""
        tab = self.tabview.tab("Fuzzing")
        tab.grid_columnconfigure(0, weight=1)

        # Title label
        title = ctk.CTkLabel(
            tab, text="PDF Fuzzing", font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Main frame for controls
        frame = ctk.CTkFrame(tab)
        frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)

        # Input directory selection
        input_label = ctk.CTkLabel(frame, text="Input directory:")
        input_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.input_entry = ctk.CTkEntry(frame, width=300)
        self.input_entry.insert(0, self.fuzz_executor.input_dir)
        self.input_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        input_button = ctk.CTkButton(
            frame, text="Browse", width=100, command=self.browse_input_dir
        )
        input_button.grid(row=0, column=2, padx=10, pady=10)

        # Target binary
        target_label = ctk.CTkLabel(frame, text="Target binary:")
        target_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.target_entry = ctk.CTkEntry(frame, width=300)
        self.target_entry.insert(0, self.fuzz_executor.xpdf_bin)
        self.target_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        target_button = ctk.CTkButton(
            frame, text="Browse", width=100, command=self.browse_target
        )
        target_button.grid(row=1, column=2, padx=10, pady=10)

        # Timeout
        timeout_label = ctk.CTkLabel(frame, text="Timeout (seconds):")
        timeout_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.timeout_entry = ctk.CTkEntry(frame, width=100)
        self.timeout_entry.insert(0, "100")
        self.timeout_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Fuzzing buttons
        button_frame = ctk.CTkFrame(frame)
        button_frame.grid(row=3, column=0, columnspan=3, padx=20, pady=20)

        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start Fuzzing",
            fg_color="green",
            hover_color="dark green",
            command=self.start_fuzzing,
        )
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = ctk.CTkButton(
            button_frame,
            text="Stop Fuzzing",
            fg_color="red",
            hover_color="dark red",
            state="disabled",
            command=self.stop_fuzzing,
        )
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        # Log area
        log_label = ctk.CTkLabel(tab, text="Fuzzing Log:")
        log_label.grid(row=2, column=0, padx=20, pady=(20, 5), sticky="w")

        self.fuzzing_log = ctk.CTkTextbox(tab, height=200)
        self.fuzzing_log.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")

    def setup_crashes_tab(self):
        """Setup the crashes tab"""
        tab = self.tabview.tab("Crashes")
        tab.grid_columnconfigure(0, weight=1)

        # Title label
        title = ctk.CTkLabel(
            tab, text="Crash Analysis", font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Crashes directory selection
        dir_frame = ctk.CTkFrame(tab)
        dir_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        dir_frame.grid_columnconfigure(1, weight=1)

        dir_label = ctk.CTkLabel(dir_frame, text="Crashes directory:")
        dir_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.crashes_dir_entry = ctk.CTkEntry(dir_frame, width=300)
        self.crashes_dir_entry.insert(0, self.fuzz_executor.output_crashes_dir)
        self.crashes_dir_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        dir_button = ctk.CTkButton(
            dir_frame, text="Browse", width=100, command=self.browse_crashes_dir
        )
        dir_button.grid(row=0, column=2, padx=10, pady=10)

        # Control frame
        control_frame = ctk.CTkFrame(tab)
        control_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        refresh_button = ctk.CTkButton(
            control_frame, text="Refresh Crashes", command=self.refresh_crashes
        )
        refresh_button.grid(row=0, column=0, padx=10, pady=10)

        self.analyze_button = ctk.CTkButton(
            control_frame,
            text="Analyze Selected",
            state="disabled",
            command=self.analyze_crash,
        )
        self.analyze_button.grid(row=0, column=1, padx=10, pady=10)

        self.debug_button = ctk.CTkButton(
            control_frame,
            text="Debug Selected",
            state="disabled",
            command=self.debug_crash,
        )
        self.debug_button.grid(row=0, column=2, padx=10, pady=10)

        # Crashes list
        self.crashes_frame = ctk.CTkScrollableFrame(tab, height=200)
        self.crashes_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

        # Analysis results
        results_label = ctk.CTkLabel(tab, text="Analysis Results:")
        results_label.grid(row=4, column=0, padx=20, pady=(20, 5), sticky="w")

        self.crash_analysis = ctk.CTkTextbox(tab, height=150)
        self.crash_analysis.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Initialize
        self.selected_crash = None
        self.crashes_list = []

    # Utility methods
    def browse_crashes_dir(self):
        """Browse for crashes directory"""
        directory = filedialog.askdirectory(title="Select Crashes Directory")
        if directory:
            self.crashes_dir_entry.delete(0, tk.END)
            self.crashes_dir_entry.insert(0, directory)

            # Update crash handler with new directory
            self.crash_handler = CrashHandler(directory)

            # Update debugger with new directory
            self.debugger.afl_output_dir = directory

            # Refresh the crashes list
            self.refresh_crashes()

    def update_status(self, message):
        """Update status bar message"""
        self.status_label.configure(text=f"Status: {message}")

    def change_appearance(self, new_appearance_mode):
        """Change the app appearance mode"""
        ctk.set_appearance_mode(new_appearance_mode)

    def log_message(self, textbox, message):
        """Add a message to the specified log textbox"""
        textbox.insert("0.0", f"{message}\n")

    # Generation tab methods
    def browse_template(self):
        """Browse for template PDF file"""
        filename = filedialog.askopenfilename(
            title="Select Template PDF",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
        )
        if filename:
            self.template_entry.delete(0, tk.END)
            self.template_entry.insert(0, filename)

    def generate_pdfs(self):
        """Generate PDF samples"""
        count = int(self.samples_entry.get())
        generator_type = self.generator_var.get()

        self.update_status(f"Generating {count} PDF samples...")
        self.log_message(
            self.generation_log, f"Starting generation of {count} PDF samples..."
        )
        self.progress_bar.set(0)

        # Start generation in a separate thread
        threading.Thread(
            target=self._generate_pdfs_thread,
            args=(count, generator_type),
            daemon=True,
        ).start()

    def _generate_pdfs_thread(self, count, generator_type):
        """Worker thread for PDF generation"""
        try:
            for i in range(count):
                # Update progress
                self.progress_bar.set((i + 1) / count)

                # Generate PDF
                pdf_path = run_fuzzer(
                    input_file="",
                    generator_name=generator_type,
                )

                # Log result
                self.log_message(
                    self.generation_log,
                    f"Generated sample {i + 1}/{count}: {os.path.basename(pdf_path)}",
                )

            # Reset progress and update status
            self.progress_bar.set(0)
            self.update_status("PDF generation complete")
            self.log_message(self.generation_log, "Generation completed successfully")

        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.log_message(self.generation_log, f"ERROR: {str(e)}")
            self.progress_bar.set(0)

    # Fuzzing tab methods
    def browse_input_dir(self):
        """Browse for input directory"""
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, directory)

    def browse_target(self):
        """Browse for target binary"""
        filename = filedialog.askopenfilename(
            title="Select Target Binary",
            filetypes=[("Executable Files", "*.exe *.out"), ("All Files", "*.*")],
        )
        if filename:
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, filename)

    def start_fuzzing(self):
        """Start AFL fuzzing process"""
        input_dir = self.input_entry.get()
        target = self.target_entry.get()
        timeout = int(self.timeout_entry.get())

        # Update UI state
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self._stop_fuzzing_requested = False

        self.update_status("Starting fuzzing process...")
        self.log_message(self.fuzzing_log, "Starting fuzzing process...")
        self.log_message(self.fuzzing_log, f"Input directory: {input_dir}")
        self.log_message(self.fuzzing_log, f"Target: {target}")
        self.log_message(self.fuzzing_log, f"Timeout: {timeout} seconds")

        # Start fuzzing in a separate thread
        threading.Thread(
            target=self._run_fuzzing_thread,
            args=(input_dir, target, timeout),
            daemon=True,
        ).start()

    def _run_fuzzing_thread(self, input_dir, target, timeout):
        """Worker thread for fuzzing"""
        try:
            # Set binary path if different from default
            if target != self.fuzz_executor.xpdf_bin:
                self.fuzz_executor.xpdf_bin = target

            # Run fuzzing
            result = self.fuzz_executor.run_afl_fuzzing(timeout=timeout)

            # Check result
            if result:
                self.log_message(self.fuzzing_log, "Fuzzing completed successfully")
            else:
                self.log_message(self.fuzzing_log, "Fuzzing failed or was stopped")

            # Reset UI state
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.update_status("Fuzzing complete")

            # Refresh crashes
            self.refresh_crashes()

        except Exception as e:
            self.log_message(self.fuzzing_log, f"ERROR: {str(e)}")
            self.update_status(f"Error: {str(e)}")
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")

    def stop_fuzzing(self):
        """Stop the fuzzing process"""
        self._stop_fuzzing_requested = True
        self.update_status("Stopping fuzzing process...")
        self.log_message(self.fuzzing_log, "Stopping fuzzing process...")

        # Find and terminate the AFL process
        try:
            import signal

            import psutil

            # Look for afl-fuzz process
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    # Check if this is an afl-fuzz process
                    if proc.info["name"] == "afl-fuzz" or (
                        proc.info["cmdline"]
                        and "afl-fuzz" in " ".join(proc.info["cmdline"])
                    ):
                        # Kill the process
                        self.log_message(
                            self.fuzzing_log,
                            f"Terminating AFL process (PID: {proc.info['pid']})",
                        )
                        os.kill(proc.info["pid"], signal.SIGTERM)

                        # Wait briefly to ensure process is terminated
                        try:
                            psutil.Process(proc.info["pid"]).wait(timeout=2)
                            self.log_message(
                                self.fuzzing_log, "AFL process terminated successfully"
                            )
                        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                            pass
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    pass

            # Update UI state immediately since we're manually stopping
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.update_status("Fuzzing stopped")

        except ImportError:
            self.log_message(
                self.fuzzing_log,
                "Error: psutil module not found. Cannot automatically terminate AFL process.",
            )
            self.log_message(
                self.fuzzing_log, "Please install psutil with: pip install psutil"
            )
            self.update_status("Error: Cannot stop fuzzing (psutil required)")
        except Exception as e:
            self.log_message(self.fuzzing_log, f"Error stopping fuzzing: {str(e)}")

    # Crashes tab methods
    def refresh_crashes(self):
        """Refresh the list of crashes"""
        # Clear existing list
        for widget in self.crashes_frame.winfo_children():
            widget.destroy()

        # Get crashes from crash handler
        crashes_dir = self.crashes_dir_entry.get()

        # Update crash handler with current directory
        if crashes_dir != self.crash_handler.output_dir:
            self.crash_handler = CrashHandler(crashes_dir)

            # Also update debugger
            self.debugger.afl_output_dir = crashes_dir

        self.crashes_list = self.crash_handler.get_crash_files()

        if not self.crashes_list:
            # No crashes found
            no_crashes = ctk.CTkLabel(
                self.crashes_frame, text="No crashes found", font=ctk.CTkFont(size=14)
            )
            no_crashes.pack(padx=20, pady=20)

            self.analyze_button.configure(state="disabled")
            self.debug_button.configure(state="disabled")
            self.selected_crash = None
            return

        # Add crashes to list
        for i, crash_file in enumerate(self.crashes_list):
            crash_frame = ctk.CTkFrame(self.crashes_frame)
            crash_frame.pack(fill="x", padx=5, pady=2, expand=True)

            # Radio button for selection
            var = ctk.IntVar()
            radio = ctk.CTkRadioButton(
                crash_frame,
                text="",
                variable=var,
                value=i,
                command=lambda idx=i: self.select_crash(idx),
            )
            radio.grid(row=0, column=0, padx=5, pady=5)

            # Crash filename
            filename = os.path.basename(crash_file)
            crash_label = ctk.CTkLabel(crash_frame, text=filename)
            crash_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.update_status(f"Found {len(self.crashes_list)} crashes")

    def select_crash(self, index):
        """Select a crash file"""
        self.selected_crash = self.crashes_list[index]
        self.analyze_button.configure(state="normal")
        self.debug_button.configure(state="normal")
        self.update_status(f"Selected crash: {os.path.basename(self.selected_crash)}")

    def analyze_crash(self):
        """Analyze selected crash"""
        if not self.selected_crash:
            return

        self.update_status("Analyzing crash...")
        self.crash_analysis.delete("0.0", "end")

        try:
            # Use crash handler to analyze
            analysis = self.crash_handler.analyze_crash_file(self.selected_crash)

            # Display results
            self.crash_analysis.insert("0.0", "Crash Analysis Results:\n\n")
            for key, value in analysis.items():
                self.crash_analysis.insert("end", f"{key}: {value}\n")

            self.update_status("Crash analysis complete")

        except Exception as e:
            self.crash_analysis.insert("0.0", f"ERROR: {str(e)}\n")
            self.update_status(f"Error: {str(e)}")

    def debug_crash(self):
        """Debug selected crash"""
        if not self.selected_crash:
            return

        self.update_status(f"Debugging crash: {os.path.basename(self.selected_crash)}")

        try:
            # Use debugger to debug crash
            self.debugger.debug_crash(self.selected_crash)
            self.update_status("Debugger launched")

        except Exception as e:
            self.crash_analysis.insert("0.0", f"ERROR launching debugger: {str(e)}\n")
            self.update_status(f"Error: {str(e)}")


def main():
    app = PyDFuzzGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
