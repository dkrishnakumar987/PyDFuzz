import os
import unittest

from pydfuzz.pdf_generator.corrupt_stream import CorruptStreamPDFGenerator


class TestCorruptStreamPDFGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = CorruptStreamPDFGenerator()
        # Generate a fresh PDF for each test method.
        self.pdf_path = self.generator.generate_pdf()

    def tearDown(self):
        if os.path.exists(self.pdf_path):
            os.remove(self.pdf_path)

    def test_pdf_generation_and_exists(self):
        # Confirm that the PDF file exists and is non-empty.
        self.assertTrue(os.path.exists(self.pdf_path), "PDF file should exist.")
        self.assertTrue(
            os.path.getsize(self.pdf_path) > 0, "PDF file should not be empty."
        )

    def test_stream_not_corrupted_before(self):
        # Verify that before corruption, the file does not contain the mis-labeled end marker.
        with open(self.pdf_path, "rb") as f:
            content = f.read().decode("utf-8", errors="ignore")
        self.assertIn(
            "endstream", content, "PDF should have proper endstream markers originally."
        )
        self.assertNotIn(
            "endstram",
            content,
            "PDF should not contain mis-labeled end marker before corruption.",
        )

    def test_corrupt_stream(self):
        # Corrupt the PDF streams.
        self.generator.corrupt_pdf(self.pdf_path)
        with open(self.pdf_path, "rb") as f:
            corrupted_content = f.read().decode("utf-8", errors="ignore")
        self.assertIn(
            "endstram",
            corrupted_content,
            "Corrupted PDF should contain mis-labeled end marker 'endstram'.",
        )

        # Check that at least one stream block has been significantly corrupted.
        markers = corrupted_content.split("stream")
        long_corruption_found = any(
            len(block.split("endstram")[0].strip()) > 1000
            for block in markers
            if "endstram" in block
        )
        self.assertTrue(
            long_corruption_found, "Corrupted stream data seems insufficient."
        )


if __name__ == "__main__":
    unittest.main()
