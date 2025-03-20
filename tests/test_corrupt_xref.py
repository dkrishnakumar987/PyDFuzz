import os
import unittest

from pydfuzz.pdf_generator.corrupt_xref import CorruptXrefPDFGenerator


class TestCorruptXrefPDFGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = CorruptXrefPDFGenerator()
        # Generate the PDF once in setUp and save its file path.
        cls.pdf_path = cls.generator.generate_pdf()

    # @classmethod
    # def tearDownClass(cls):
    #     # Clean up the generated PDF file.
    #     if os.path.exists(cls.pdf_path):
    #         os.remove(cls.pdf_path)
    #
    # def test_pdf_header_and_footer(self):
    #     print(self.__class__.pdf_path)
    #     # Open the saved PDF and check its header and footer.
    #     with open(self.__class__.pdf_path, "rb") as f:
    #         pdf_content = f.read().decode("utf-8", errors="ignore")
    #     self.assertTrue(pdf_content.startswith("%PDF-"), "PDF header is incorrect.")
    #     self.assertTrue(
    #         pdf_content.strip().endswith("%%EOF"), "PDF footer is incorrect."
    #     )
    #
    def test_save_pdf(self):
        print(self.__class__.pdf_path)
        # As the PDF is generated once in setUp, verify that it exists and is non-empty.
        self.assertTrue(
            os.path.exists(self.__class__.pdf_path),
            "Saved PDF file should exist.",
        )
        self.assertTrue(
            os.path.getsize(self.__class__.pdf_path) > 0,
            "Saved PDF file should not be empty.",
        )

    def test_corrupted_xref(self):
        print(self.__class__.pdf_path)
        # Corrupt the generated PDF.
        self.__class__.generator.corrupt_pdf(self.__class__.pdf_path)
        with open(self.__class__.pdf_path, "rb") as f:
            pdf_content = f.read().decode("utf-8", errors="ignore")
        # Verify that the xref section is present.
        self.assertIn(
            "xref", pdf_content, "xref section is missing in corrupted PDF."
        )
        # Grab and validate the startxref value.
        lines = pdf_content.splitlines()
        try:
            idx = lines.index("startxref")
            startxref_val = lines[idx + 1].strip()
        except (ValueError, IndexError):
            self.fail("No valid startxref value found.")
        self.assertNotEqual(
            startxref_val, "", "startxref value should be non-empty"
        )
        try:
            int(startxref_val)
            valid = True
        except ValueError:
            valid = startxref_val == "CORRUPT"
        self.assertTrue(
            valid, "startxref must be a number or the string 'CORRUPT'."
        )


if __name__ == "__main__":
    unittest.main()
