import os
import subprocess
import argparse
import glob
from typing import List, Optional

from pydfuzz.logger import logger


class FuzzDebugger:
    """
    Debug crashes and hangs discovered by AFL++ fuzzing using GDB.
    """

    def __init__(
        self,
        binary_path: str,
        output_dir: str = "./output",
        afl_output_dir: Optional[str] = None,
    ):
        """
        Initialize the fuzzing debugger.

        Args:
            binary_path: Path to the binary executable
            output_dir: Directory where the binary writes its output (not AFL output)
            afl_output_dir: Directory where AFL stored crashes/hangs
        """
        self.binary_path = os.path.abspath(binary_path)
        self.output_dir = os.path.abspath(output_dir)

        # If no AFL output dir is provided, use the default project location
        if afl_output_dir is None:
            # Get project root directory
            project_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..")
            )
            self.afl_output_dir = os.path.join(project_root, "output_crashes")
        else:
            self.afl_output_dir = os.path.abspath(afl_output_dir)

        # Ensure the binary exists
        if not os.path.isfile(self.binary_path):
            logger.error(f"Binary not found at: {self.binary_path}")
            raise FileNotFoundError(f"Binary not found at: {self.binary_path}")

        # Ensure the AFL output directory exists
        if not os.path.isdir(self.afl_output_dir):
            logger.error(f"AFL output directory not found: {self.afl_output_dir}")
            raise FileNotFoundError(
                f"AFL output directory not found: {self.afl_output_dir}"
            )

        logger.info(f"Debugger initialized with binary: {self.binary_path}")
        logger.info(f"AFL output directory: {self.afl_output_dir}")

    def get_crashes(self) -> List[str]:
        """
        Get list of crash files found by AFL.

        Returns:
            List of paths to crash files
        """
        crashes = []

        # Look in default/crashes directory
        crash_path = os.path.join(self.afl_output_dir, "default", "crashes")
        if os.path.isdir(crash_path):
            crashes.extend(glob.glob(os.path.join(crash_path, "id:*")))

        # Also look directly in the crashes directory (alternate structure)
        if os.path.isdir(os.path.join(self.afl_output_dir, "crashes")):
            crashes.extend(
                glob.glob(os.path.join(self.afl_output_dir, "crashes", "id:*"))
            )

        return crashes

    def get_hangs(self) -> List[str]:
        """
        Get list of hang files found by AFL.

        Returns:
            List of paths to hang files
        """
        hangs = []

        # Look in default/hangs directory
        hang_path = os.path.join(self.afl_output_dir, "default", "hangs")
        if os.path.isdir(hang_path):
            hangs.extend(glob.glob(os.path.join(hang_path, "id:*")))

        # Also look directly in the hangs directory (alternate structure)
        if os.path.isdir(os.path.join(self.afl_output_dir, "hangs")):
            hangs.extend(glob.glob(os.path.join(self.afl_output_dir, "hangs", "id:*")))

        return hangs

    def debug_crash(self, crash_file: str) -> None:
        """
        Debug a specific crash file with GDB.

        Args:
            crash_file: Path to the crash file
        """
        if not os.path.isfile(crash_file):
            logger.error(f"Crash file not found: {crash_file}")
            raise FileNotFoundError(f"Crash file not found: {crash_file}")

        # Create the GDB command
        gdb_cmd = f"gdb --args {self.binary_path} {crash_file} {self.output_dir}"

        # Create a GDB script with startup commands
        gdb_script = "/tmp/pydfuzz_gdb_script"
        with open(gdb_script, "w") as f:
            f.write("run\n")  # Add the run command

        # Use x-terminal-emulator (standard terminal launcher) to open a new terminal
        # Pass the GDB command and script
        term_cmd = [
            "x-terminal-emulator",
            "-e",
            f"gdb -x {gdb_script} --args {self.binary_path} {crash_file} {self.output_dir}",
        ]

        # Alternative methods for different platforms:
        if not self._is_command_available("x-terminal-emulator"):
            if self._is_command_available("gnome-terminal"):
                term_cmd = [
                    "gnome-terminal",
                    "--",
                    f"gdb -x {gdb_script} --args {self.binary_path} {crash_file} {self.output_dir}",
                ]
            elif self._is_command_available("xterm"):
                term_cmd = [
                    "xterm",
                    "-e",
                    f"gdb -x {gdb_script} --args {self.binary_path} {crash_file} {self.output_dir}",
                ]
            elif self._is_command_available("konsole"):
                term_cmd = [
                    "konsole",
                    "-e",
                    f"gdb -x {gdb_script} --args {self.binary_path} {crash_file} {self.output_dir}",
                ]
            else:
                logger.warning(
                    "No supported terminal emulator found. Launching GDB directly."
                )
                term_cmd = [
                    "gdb",
                    "-x",
                    gdb_script,
                    "--args",
                    self.binary_path,
                    crash_file,
                    self.output_dir,
                ]

        logger.info(f"Launching GDB with command: {' '.join(term_cmd)}")

        try:
            subprocess.Popen(term_cmd)
            logger.info(f"GDB launched for crash file: {os.path.basename(crash_file)}")
        except Exception as e:
            logger.error(f"Failed to launch GDB: {e}")
            # Fallback to direct GDB if terminal launch fails
            try:
                gdb_cmd = [
                    "gdb",
                    "-x",
                    gdb_script,
                    "--args",
                    self.binary_path,
                    crash_file,
                    self.output_dir,
                ]
                subprocess.Popen(gdb_cmd)
            except Exception as e:
                logger.error(f"Failed to launch GDB directly: {e}")

    def _is_command_available(self, cmd: str) -> bool:
        """
        Check if a command is available in the system's PATH.

        Args:
            cmd: Command to check

        Returns:
            True if available, False otherwise
        """
        try:
            devnull = open(os.devnull, "w")
            subprocess.call([cmd, "--version"], stdout=devnull, stderr=devnull)
            return True
        except (OSError, subprocess.SubprocessError):
            return False


def main():
    parser = argparse.ArgumentParser(description="Debug AFL++ crashes with GDB")
    parser.add_argument(
        "-b",
        "--binary",
        default=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "fuzz_build/xpdf-3.02/build/release/bin/pdftotext",
        ),
        help="Path to target binary",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="./output",
        help="Directory for program output (not AFL output)",
    )
    parser.add_argument(
        "-a",
        "--afl-output",
        default=None,
        help="Path to AFL++ output directory (defaults to project's output_crashes)",
    )
    parser.add_argument(
        "-c", "--crash-id", help="Specific crash ID to debug (e.g. id:000000)"
    )
    parser.add_argument(
        "-l", "--list", action="store_true", help="List available crashes and hangs"
    )

    args = parser.parse_args()

    try:
        debugger = FuzzDebugger(args.binary, args.output_dir, args.afl_output)

        # List mode - just show available crashes and exit
        if args.list:
            crashes = debugger.get_crashes()
            hangs = debugger.get_hangs()

            print("\n=== Available Crashes and Hangs ===")

            if crashes:
                print("\nCrashes:")
                for i, crash in enumerate(crashes, 1):
                    print(f"{i}. {os.path.basename(crash)}")
            else:
                print("\nNo crashes found.")

            if hangs:
                print("\nHangs:")
                for i, hang in enumerate(hangs, 1):
                    print(f"{i}. {os.path.basename(hang)}")
            else:
                print("\nNo hangs found.")

            return 0

        # Debug specific crash
        if args.crash_id:
            # Try different paths to find the crash
            crash_paths = [
                # Default structure with subfolder
                os.path.join(
                    debugger.afl_output_dir, "default", "crashes", args.crash_id
                ),
                # Alternative structure without subfolder
                os.path.join(debugger.afl_output_dir, "crashes", args.crash_id),
                # If user provided a full filename with id: prefix
                os.path.join(
                    debugger.afl_output_dir, "default", "crashes", args.crash_id
                ),
                # Allow direct path
                args.crash_id,
            ]

            for path in crash_paths:
                if os.path.isfile(path):
                    debugger.debug_crash(path)
                    return 0

            # If we get here, we couldn't find the crash
            logger.error(f"Could not find crash with ID: {args.crash_id}")
            print(f"Could not find crash with ID: {args.crash_id}")
            print("Use --list to see available crashes")
            return 1

        # No crash specified, use first available crash
        else:
            crashes = debugger.get_crashes()
            if crashes:
                debugger.debug_crash(crashes[0])
                return 0
            else:
                logger.error("No crashes found to debug")
                print("No crashes found to debug")
                print("Run AFL++ fuzzing first or check the output directory")
                return 1

    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
