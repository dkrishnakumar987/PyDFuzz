import os
import unittest
import re
from pydfuzz.pdf_generator.corrupt_javascript import CorruptJavaScriptPDFGenerator


class TestCorruptJavaScriptPDFGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = CorruptJavaScriptPDFGenerator()
        # Generate a PDF and store its file path.
        cls.pdf_path = cls.generator.generate_pdf()

    @classmethod
    def tearDownClass(cls):
        # Remove the generated PDF file.
        if os.path.exists(cls.pdf_path):
            os.remove(cls.pdf_path)

    def test_js_injection_exists(self):
        # First, corrupt the PDF by injecting the malicious JavaScript.
        self.__class__.generator.corrupt_pdf(self.__class__.pdf_path)
        with open(self.__class__.pdf_path, "rb") as f:
            content = f.read().decode("utf-8", errors="ignore")

        # Verify that the JavaScript object marker (object number "100 0 obj") is present.
        self.assertIn(
            "100 0 obj",
            content,
            "Corrupted PDF does not contain the injected JS object.",
        )

        # Verify that the object contains a JavaScript action.
        self.assertIn(
            "/S /JavaScript",
            content,
            "Injected JS object is missing the JavaScript action marker.",
        )

        # Check that a malicious payload is present by looking for "while(true){};".
        # Since the payload is repeated many times, a simple regex search is used.
        payload_matches = re.findall(r"while\(true\)\{\}\;", content)
        self.assertTrue(
            len(payload_matches) > 0,
            "Malicious JavaScript payload not found in the corrupted PDF.",
        )

        # Optionally, verify that the injection occurred before the trailer.
        trailer_index = content.find("trailer")
        js_obj_index = content.find("100 0 obj")
        self.assertGreater(
            trailer_index,
            js_obj_index,
            "Injected JS object should appear before the trailer section.",
        )


if __name__ == "__main__":
    unittest.main()
