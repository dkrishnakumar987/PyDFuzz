import os
import re
from typing import Dict, List

from pydfuzz.logger import logger


class CrashHandler:
    """
    Handles and analyzes crashes and hangs found during AFL++ fuzzing.
    """

    def __init__(self, output_dir: str):
        """
        Initialize the crash handler with the path to AFL++ output directory.

        Args:
            output_dir: Path to the AFL++ output directory
        """
        self.output_dir = os.path.abspath(output_dir)

        if not os.path.isdir(self.output_dir):
            logger.error(f"Output directory not found: {self.output_dir}")
            raise FileNotFoundError(f"Output directory not found: {self.output_dir}")

        logger.info(f"Analyzing crash data in {self.output_dir}")

    def get_fuzzer_stats(self) -> Dict:
        """
        Parse the fuzzer_stats file to get statistics about the fuzzing run.

        Returns:
            Dict containing fuzzer statistics
        """
        stats = {}
        fuzzer_dirs = self._get_fuzzer_dirs()

        for fuzzer_dir in fuzzer_dirs:
            stats_file = os.path.join(fuzzer_dir, "fuzzer_stats")
            if os.path.isfile(stats_file):
                fuzzer_name = os.path.basename(fuzzer_dir)
                stats[fuzzer_name] = {}

                with open(stats_file, "r") as f:
                    for line in f:
                        if ":" in line:
                            key, value = line.strip().split(":", 1)
                            stats[fuzzer_name][key.strip()] = value.strip()

        return stats

    def get_crash_files(self) -> List[str]:
        """
        Find all crash files in the output directory.

        Returns:
            List of paths to crash files
        """
        crash_files = []
        fuzzer_dirs = self._get_fuzzer_dirs()

        for fuzzer_dir in fuzzer_dirs:
            crashes_dir = os.path.join(fuzzer_dir, "crashes")
            if os.path.isdir(crashes_dir):
                for file in os.listdir(crashes_dir):
                    # Skip README.txt and other non-crash files
                    if file != "README.txt" and not file.startswith("."):
                        crash_files.append(os.path.join(crashes_dir, file))

        return crash_files

    def get_hang_files(self) -> List[str]:
        """
        Find all hang files in the output directory.

        Returns:
            List of paths to hang files
        """
        hang_files = []
        fuzzer_dirs = self._get_fuzzer_dirs()

        for fuzzer_dir in fuzzer_dirs:
            hangs_dir = os.path.join(fuzzer_dir, "hangs")
            if os.path.isdir(hangs_dir):
                for file in os.listdir(hangs_dir):
                    # Skip README.txt and other non-hang files
                    if file != "README.txt" and not file.startswith("."):
                        hang_files.append(os.path.join(hangs_dir, file))

        return hang_files

    def analyze_crash_file(self, crash_file: str) -> Dict:
        """
        Analyze a crash file to extract useful information.

        Args:
            crash_file: Path to the crash file

        Returns:
            Dict with crash analysis
        """
        info = {
            "path": crash_file,
            "filename": os.path.basename(crash_file),
            "size": os.path.getsize(crash_file),
            "type": "crash",
        }

        # Try to extract more information from AFL++ filename
        match = re.search(
            r"id:(\d+),src:([^,]+),time:(\d+),execs:(\d+),op:([^,]+),rep:(\d+)",
            os.path.basename(crash_file),
        )
        if match:
            info["id"] = match.group(1)
            info["source"] = match.group(2)
            info["time"] = int(match.group(3))
            info["executions"] = int(match.group(4))
            info["operation"] = match.group(5)
            info["repetitions"] = int(match.group(6))

        return info

    def summarize(self) -> Dict:
        """
        Provide a summary of all crashes and hangs.

        Returns:
            Dict containing summary information
        """
        crash_files = self.get_crash_files()
        hang_files = self.get_hang_files()
        stats = self.get_fuzzer_stats()

        # Get the first available fuzzer stats for overall info
        overall_stats = next(iter(stats.values())) if stats else {}

        summary = {
            "total_crashes": len(crash_files),
            "total_hangs": len(hang_files),
            "fuzzer_stats": stats,
            "run_time_seconds": int(overall_stats.get("run_time", 0))
            if overall_stats
            else 0,
            "execs_per_sec": float(overall_stats.get("execs_per_sec", 0))
            if overall_stats
            else 0,
            "total_executions": int(overall_stats.get("execs_done", 0))
            if overall_stats
            else 0,
            "crashes": [
                self.analyze_crash_file(f) for f in crash_files[:10]
            ],  # Limit to 10 for brevity
            "hangs": [
                self.analyze_crash_file(f) for f in hang_files[:10]
            ],  # Limit to 10 for brevity
        }

        return summary

    def display_summary(self) -> None:
        """
        Display a summary of crashes and hangs to the console.
        """
        summary = self.summarize()

        print("\n===== AFL++ Fuzzing Results Summary =====")
        print(f"Total crashes found: {summary['total_crashes']}")
        print(f"Total hangs found: {summary['total_hangs']}")
        print(f"Total execution time: {summary['run_time_seconds']} seconds")
        print(f"Executions per second: {summary['execs_per_sec']:.2f}")
        print(f"Total executions: {summary['total_executions']}")

        if summary["crashes"]:
            print("\n----- Top Crashes -----")
            for i, crash in enumerate(summary["crashes"], 1):
                print(f"{i}. {crash['filename']} - Size: {crash['size']} bytes")

        if summary["hangs"]:
            print("\n----- Top Hangs -----")
            for i, hang in enumerate(summary["hangs"], 1):
                print(f"{i}. {hang['filename']} - Size: {hang['size']} bytes")

    def _get_fuzzer_dirs(self) -> List[str]:
        """
        Find all fuzzer directories in the output directory.

        Returns:
            List of paths to fuzzer directories
        """
        fuzzer_dirs = []

        # If the directory contains fuzzer_stats, it's a fuzzer directory itself
        if os.path.isfile(os.path.join(self.output_dir, "fuzzer_stats")):
            fuzzer_dirs.append(self.output_dir)

        # Otherwise, look for subdirectories
        for item in os.listdir(self.output_dir):
            item_path = os.path.join(self.output_dir, item)
            if os.path.isdir(item_path) and os.path.isfile(
                os.path.join(item_path, "fuzzer_stats")
            ):
                fuzzer_dirs.append(item_path)

        return fuzzer_dirs
