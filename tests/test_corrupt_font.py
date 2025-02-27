import os
import re
import unittest
from pydfuzz.pdf_generator.corrupt_font import CorruptFontPDFGenerator


class TestCorruptFontPDFGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = CorruptFontPDFGenerator()
        # Generate a PDF file.
        self.pdf_path = self.generator.generate_pdf()

    def tearDown(self):
        if os.path.exists(self.pdf_path):
            os.remove(self.pdf_path)

    def test_font_names_corrupted(self):
        # List of common fonts expected in a valid PDF.
        common_fonts = ["Helvetica", "Times", "Courier", "Symbol", "ZapfDingbats"]

        # Read the generated PDF content before corruption.
        with open(self.pdf_path, "rb") as f:
            content_before = f.read().decode("utf-8", errors="ignore")

        # Verify that at least one common font is present before corruption.
        found_font = any(
            re.search(r"/" + font + r"\b", content_before) for font in common_fonts
        )
        self.assertTrue(
            found_font,
            "The generated PDF should contain at least one common font before corruption.",
        )

        # Now corrupt the PDF.
        self.generator.corrupt_pdf(self.pdf_path)

        # Read the PDF content after corruption.
        with open(self.pdf_path, "rb") as f:
            content_after = f.read().decode("utf-8", errors="ignore")

        # Verify that none of the common fonts remain.
        for font in common_fonts:
            self.assertNotRegex(
                content_after,
                r"/" + font + r"\b",
                msg=f"Font {font} should be corrupted and not present in the PDF.",
            )

        # Optionally, verify that font resource names (e.g. /F1, /F2) have been replaced.
        self.assertNotRegex(
            content_after,
            r"/F\d+\b",
            msg="Font resource names should be corrupted and not present.",
        )


if __name__ == "__main__":
    unittest.main()
