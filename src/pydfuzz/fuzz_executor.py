import os
import subprocess
from typing import Optional

from pydfuzz.logger import logger


class FuzzExecutor:
    """
    Executes fuzzing against PDF processing binaries using AFL++.
    """

    def __init__(self):
        # Get project root directory
        self.project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )

        # Set up directories
        self.input_dir = os.path.join(self.project_root, "input_pdfs")
        self.output_crashes_dir = os.path.join(self.project_root, "output_crashes")
        self.output_dir = os.path.join(self.project_root, "output")

        # Create directories if they don't exist
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_crashes_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        # Path to the xpdf binary
        self.xpdf_bin = os.path.join(
            self.project_root, "fuzz_build/xpdf-3.02/build/release/bin/pdftotext"
        )

        # Ensure the binary exists
        if not os.path.isfile(self.xpdf_bin):
            logger.error(f"xpdf binary not found at: {self.xpdf_bin}")
            raise FileNotFoundError(f"xpdf binary not found at: {self.xpdf_bin}")

    def run_afl_fuzzing(
        self,
        timeout: Optional[int] = None,
        seed: int = 123,
        deterministic: bool = False,
    ) -> bool:
        """
        Execute AFL++ fuzzing against the xpdf pdftotext binary.

        Args:
            timeout: Maximum time to run fuzzing in seconds (None for no timeout)
            seed: Random seed for reproducibility
            deterministic: Whether to use deterministic fuzzing mode

        Returns:
            bool: True if fuzzing completed successfully, False otherwise
        """
        logger.info(f"Starting AFL fuzzing with seed {seed}")

        # Construct AFL command
        cmd = [
            "afl-fuzz",
            "-i",
            self.input_dir,
            "-o",
            self.output_crashes_dir,
            "-s",
            str(seed),
            "-P",
            "exploit",
        ]

        # Add deterministic flag if required
        if deterministic:
            cmd.append("-D")

        # Add target command
        cmd.extend(["--", self.xpdf_bin, "@@", "./output"])

        logger.debug(f"Running command: {' '.join(cmd)}")

        # Set up environment variables for AFL
        env = os.environ.copy()
        env["AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES"] = (
            "1"  # Suppress warnings about missing crashes
        )
        env["AFL_SKIP_CPUFREQ"] = (
            "1"  # Skip CPU frequency check that might cause issues
        )

        try:
            # Execute the command with the modified environment
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                env=env,  # Pass the environment variables
            )

            # Wait for process to complete if timeout specified
            if timeout:
                try:
                    stdout, stderr = process.communicate(timeout=timeout)
                    logger.debug(
                        f"AFL process finished with return code {process.returncode}"
                    )
                    if process.returncode != 0:
                        logger.error(f"AFL process failed: {stderr}")
                        return False
                except subprocess.TimeoutExpired:
                    logger.info(f"AFL fuzzing stopped after timeout ({timeout}s)")
                    process.terminate()
                    process.wait()
            else:
                # If no timeout, just let it run until user interruption
                logger.info("AFL fuzzing started. Press Ctrl+C to stop.")
                process.wait()

            return True

        except KeyboardInterrupt:
            logger.info("Fuzzing interrupted by user")
            if "process" in locals():
                process.terminate()
                process.wait()
            return True

        except Exception as e:
            logger.exception(f"Error during AFL fuzzing: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    executor = FuzzExecutor()
    executor.run_afl_fuzzing()
