import re
import random
import string
from pydfuzz.pdf_generator.base_generator import BasePDFGenerator


class CorruptFontPDFGenerator(BasePDFGenerator):
    """
    Generates a PDF file and then corrupts its font definitions.
    This implementation replaces valid font names (e.g. /Helvetica, /Times, /Courier,
    /Symbol, /ZapfDingbats) with random invalid strings to induce failures in the PDF reader.
    """

    def corrupt_pdf(self, pdf_path: str) -> None:
        """
        Open the PDF at pdf_path, corrupt its font definitions by replacing font names
        for multiple commonly used fonts with random invalid strings, and write the corrupted
        PDF back to disk.

        Args:
            pdf_path (str): The file path of the PDF to be corrupted.
        """
        # Read original PDF content.
        with open(pdf_path, "rb") as f:
            content = f.read().decode("utf-8", errors="ignore")

        # List of common fonts we want to corrupt.
        common_fonts = ["Helvetica", "Times", "Courier", "Symbol", "ZapfDingbats"]

        # For each common font, generate a random corrupted version and replace it.
        for font in common_fonts:
            corrupted_font_name = "/" + "".join(
                random.choices(string.ascii_letters + string.digits, k=20)
            )
            content = re.sub(r"/" + font + r"\b", corrupted_font_name, content)

        # Optionally, also corrupt font resource names like /F1, /F2, etc.
        # Here, we replace any occurrence of /F followed by a digit with a random string.
        content = re.sub(
            r"/F\d+\b",
            lambda m: "/"
            + "".join(random.choices(string.ascii_letters + string.digits, k=8)),
            content,
        )

        # Write the corrupted content back to disk.
        with open(pdf_path, "wb") as f:
            f.write(content.encode("utf-8"))
