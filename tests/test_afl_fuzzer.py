import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from pydfuzz.afl_fuzzer import AFLLinuxFuzzer


class TestAFLLinuxFuzzer(unittest.TestCase):
    """
    Test suite for the AFLLinuxFuzzer class.

    These tests use mocking to avoid actual execution of AFL++ or MuPDF binaries.
    """

    def setUp(self):
        """Set up temporary directories and initialize the fuzzer."""
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = os.path.join(self.temp_dir, "input_pdfs")
        self.output_dir = os.path.join(self.temp_dir, "afl_output")
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        # Mock external dependencies during initialization
        with patch("shutil.which") as mock_which:
            # Simulate that afl-fuzz and mutool are available
            mock_which.side_effect = (
                lambda cmd: "/usr/bin/" + cmd if cmd in ["afl-fuzz", "mutool"] else None
            )
            self.fuzzer = AFLLinuxFuzzer(
                input_dir=self.input_dir, output_dir=self.output_dir
            )

        # Create sample PDF files for testing
        self.pdf_files = []
        for i in range(3):
            pdf_path = os.path.join(self.temp_dir, f"test_{i}.pdf")
            with open(pdf_path, "wb") as f:
                f.write(b"%PDF-1.7\nTest PDF content")
            self.pdf_files.append(pdf_path)

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)

    @patch("shutil.which")
    def test_initialization_with_missing_afl(self, mock_which):
        """Test initialization when AFL++ is not installed."""
        # Simulate afl-fuzz not being available
        mock_which.side_effect = lambda cmd: None

        # AFLLinuxFuzzer should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            AFLLinuxFuzzer(input_dir=self.input_dir, output_dir=self.output_dir)

    @patch("os.path.isfile")
    @patch("shutil.which")
    def test_locate_mupdf_binary(self, mock_which, mock_isfile):
        """Test MuPDF binary location logic."""
        # Simulate mutool not in PATH but available at a specific location
        mock_which.return_value = None
        mock_isfile.side_effect = lambda path: path == "/opt/mupdf/bin/mutool"

        with patch("shutil.which") as mock_which_init:
            mock_which_init.side_effect = (
                lambda cmd: "/usr/bin/" + cmd if cmd == "afl-fuzz" else None
            )
            fuzzer = AFLLinuxFuzzer(
                input_dir=self.input_dir, output_dir=self.output_dir
            )

        self.assertEqual(fuzzer.mupdf_bin, "/opt/mupdf/bin/mutool")

    @patch("os.path.isfile")
    @patch("shutil.which")
    def test_locate_mupdf_binary_failure(self, mock_which, mock_isfile):
        """Test MuPDF binary location failure case."""
        # Simulate mutool not found anywhere
        mock_which.return_value = None
        mock_isfile.return_value = False

        with patch("shutil.which") as mock_which_init:
            mock_which_init.side_effect = (
                lambda cmd: "/usr/bin/" + cmd if cmd == "afl-fuzz" else None
            )
            with self.assertRaises(FileNotFoundError):
                AFLLinuxFuzzer(input_dir=self.input_dir, output_dir=self.output_dir)

    def test_set_mupdf_binary(self):
        """Test setting MuPDF binary path manually."""
        # Set up a valid file path
        valid_path = os.path.join(self.temp_dir, "valid_mutool")
        with open(valid_path, "w") as f:
            f.write("#!/bin/bash\necho 'Fake MuPDF'")
        os.chmod(valid_path, 0o755)

        # Set the path
        self.fuzzer.set_mupdf_binary(valid_path)
        self.assertEqual(self.fuzzer.mupdf_bin, valid_path)

        # Test with invalid path
        invalid_path = os.path.join(self.temp_dir, "nonexistent")
        with self.assertRaises(FileNotFoundError):
            self.fuzzer.set_mupdf_binary(invalid_path)

    def test_prepare_corpus(self):
        """Test preparing the corpus from PDF files."""
        # Create some existing files in the input directory that should be removed
        old_file = os.path.join(self.input_dir, "old.pdf")
        with open(old_file, "w") as f:
            f.write("Old PDF content")

        # Non-PDF file that should be left untouched
        non_pdf = os.path.join(self.input_dir, "not_a_pdf.txt")
        with open(non_pdf, "w") as f:
            f.write("Not a PDF")

        # Prepare corpus with our sample PDFs
        self.fuzzer.prepare_corpus(self.pdf_files)

        # Check that the old PDF was removed
        self.assertFalse(os.path.exists(old_file))

        # Check that the non-PDF file was left untouched
        self.assertTrue(os.path.exists(non_pdf))

        # Check that our sample PDFs were copied
        corpus_files = [f for f in os.listdir(self.input_dir) if f.endswith(".pdf")]
        self.assertEqual(len(corpus_files), len(self.pdf_files))

        # Test with non-existent PDF
        non_existent = os.path.join(self.temp_dir, "non_existent.pdf")
        with self.assertLogs(level="WARNING") as cm:
            self.fuzzer.prepare_corpus([non_existent])
            self.assertIn("Skipping invalid file", cm.output[0])

    @patch("subprocess.Popen")
    def test_run_afl_fuzz_single(self, mock_popen):
        """Test running a single instance of AFL++."""
        # Mock the subprocess.Popen to avoid actual execution
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Fuzzing output", "")
        mock_popen.return_value = mock_process

        # Mock the parse_afl_output method
        with patch.object(self.fuzzer, "_parse_afl_output") as mock_parse:
            mock_parse.return_value = {"crashes": 2, "unique_crashes": 1}

            # Run the fuzzer with a short timeout
            results = self.fuzzer.run_afl_fuzz(timeout=10)

            # Verify the results
            self.assertEqual(results["crashes"], 2)
            self.assertEqual(results["unique_crashes"], 1)

            # Verify AFL++ was called with correct arguments
            args, _ = mock_popen.call_args
            cmd = args[0]
            self.assertEqual(cmd[0], "afl-fuzz")
            self.assertIn(self.input_dir, cmd)
            self.assertIn(self.output_dir, cmd)
            self.assertIn(self.fuzzer.mupdf_bin, cmd)
            self.assertIn("show", cmd)
            self.assertIn("@@", cmd)

    @patch("subprocess.Popen")
    def test_run_afl_fuzz_parallel(self, mock_popen):
        """Test running AFL++ in parallel mode."""
        # Mock the subprocess.Popen to avoid actual execution
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Fuzzing output", "")
        mock_popen.return_value = mock_process

        # Mock the parse method
        with patch.object(self.fuzzer, "_parse_parallel_afl_output") as mock_parse:
            mock_parse.return_value = {"total_crashes": 3, "total_unique_crashes": 2}

            # Run the fuzzer in parallel mode with a short timeout
            results = self.fuzzer.run_afl_fuzz(timeout=10, parallel=True, cores=2)

            # Verify the results
            self.assertEqual(results["total_crashes"], 3)
            self.assertEqual(results["total_unique_crashes"], 2)

            # Verify AFL++ was called with correct arguments for master and slave
            self.assertEqual(mock_popen.call_count, 2)  # Master + 1 slave

            # Check master arguments
            args, _ = mock_popen.call_args_list[0]
            cmd = args[0]
            self.assertEqual(cmd[0], "afl-fuzz")
            self.assertIn("-M", cmd)
            self.assertIn("fuzzer01", cmd)

            # Check slave arguments
            args, _ = mock_popen.call_args_list[1]
            cmd = args[0]
            self.assertEqual(cmd[0], "afl-fuzz")
            self.assertIn("-S", cmd)
            self.assertIn("fuzzer02", cmd)

    def test_run_afl_fuzz_empty_input(self):
        """Test running AFL++ with an empty input directory."""
        # Clear the input directory
        for file in os.listdir(self.input_dir):
            os.unlink(os.path.join(self.input_dir, file))

        # Running the fuzzer should raise ValueError
        with self.assertRaises(ValueError):
            self.fuzzer.run_afl_fuzz(timeout=10)

    @patch("os.path.isdir")
    @patch("os.path.isfile")
    @patch("builtins.open")
    def test_parse_afl_output(self, mock_open_func, mock_isfile, mock_isdir):
        """Test parsing AFL++ output directory."""
        # Simulate directory structure and files
        mock_isdir.side_effect = lambda path: (
            path == self.output_dir
            or path == os.path.join(self.output_dir, "default")
            or path == os.path.join(self.output_dir, "default", "crashes")
            or path == os.path.join(self.output_dir, "default", "hangs")
        )

        mock_isfile.side_effect = lambda path: (
            path == os.path.join(self.output_dir, "default", "fuzzer_stats")
        )

        # Fixed issue: Properly mock file content for line-by-line reading
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.__iter__.return_value = iter(
            ["unique_crashes : 3\n", "execs_per_sec : 100.5\n", "paths_total : 42\n"]
        )
        mock_open_func.return_value = mock_file

        # Simulate crash files
        with patch("os.listdir") as mock_listdir:
            mock_listdir.side_effect = lambda path: (
                []
                if path == self.output_dir
                else ["fuzzer_stats"]
                if path == os.path.join(self.output_dir, "default")
                else ["crash_1", "crash_2", "README.txt"]
                if path == os.path.join(self.output_dir, "default", "crashes")
                else ["hang_1", "README.txt"]
                if path == os.path.join(self.output_dir, "default", "hangs")
                else []
            )

            # Parse output
            results = self.fuzzer._parse_afl_output()

            # Verify results
            self.assertEqual(results["unique_crashes"], 3)
            self.assertEqual(results["execs_per_sec"], 100.5)
            self.assertEqual(results["paths_total"], 42)
            self.assertEqual(results["crashes"], 2)  # README.txt is excluded
            self.assertEqual(results["hangs"], 1)  # README.txt is excluded

    @patch("os.path.isdir")
    @patch("os.listdir")
    def test_get_crash_files(self, mock_listdir, mock_isdir):
        """Test retrieving crash files."""
        # Simulate directory structure
        mock_isdir.side_effect = lambda path: (
            path == self.output_dir
            or path == os.path.join(self.output_dir, "default", "crashes")
            or path == os.path.join(self.output_dir, "fuzzer01", "crashes")
        )

        # Simulate crash files
        mock_listdir.side_effect = lambda path: (
            ["default", "fuzzer01"]
            if path == self.output_dir
            else ["crash_1", "crash_2", "README.txt"]
            if path == os.path.join(self.output_dir, "default", "crashes")
            else ["crash_3", "README.txt"]
            if path == os.path.join(self.output_dir, "fuzzer01", "crashes")
            else []
        )

        # Get crash files
        crash_files = self.fuzzer.get_crash_files()

        # Verify the number of crash files (excluding README.txt)
        self.assertEqual(len(crash_files), 3)

        # Verify paths
        expected_paths = [
            os.path.join(self.output_dir, "default", "crashes", "crash_1"),
            os.path.join(self.output_dir, "default", "crashes", "crash_2"),
            os.path.join(self.output_dir, "fuzzer01", "crashes", "crash_3"),
        ]
        self.assertCountEqual(crash_files, expected_paths)


if __name__ == "__main__":
    unittest.main()
