import re
import random
import string
from pydfuzz.pdf_generator.base_generator import BasePDFGenerator


class CorruptStreamPDFGenerator(BasePDFGenerator):
    """
    Generates a PDF file and then corrupts its content streams.
    Inherits PDF generation from BasePDFGenerator and corrupts the stream content
    by replacing it with an enormous random string and mislabeling the end marker,
    which is likely to crash a PDF reader.
    """

    def corrupt_pdf(self, pdf_path: str) -> None:
        """
        Open the PDF at pdf_path, corrupt its stream contents by injecting a huge amount
        of random data and altering the endstream marker, and write the corrupted PDF
        back to disk.

        Args:
            pdf_path (str): The file path of the PDF to be corrupted.
        """
        # Read the original PDF content as text.
        with open(pdf_path, "rb") as f:
            content = f.read().decode("utf-8", errors="ignore")

        # Regular expression to match stream blocks.
        # The pattern captures the header ("stream" plus newline), the stream's contents,
        # and the footer (newline followed by "endstream").
        pattern = re.compile(r"(stream\s*\n)(.*?)(\nendstream)", re.DOTALL)

        def corrupt_match(match):
            header = match.group(1)
            # Inject a huge random string to overwhelm the PDF reader.
            corrupted_content = "".join(
                random.choices(string.ascii_letters + string.digits, k=1000000)
            )
            # Deliberately mislabel the end marker to "endstram" (missing the 'e').
            footer = "\nendstram"
            return f"{header}{corrupted_content}{footer}"

        # Replace all stream blocks with the corrupted version.
        corrupted_pdf = pattern.sub(corrupt_match, content)

        # Write the corrupted PDF back to disk.
        with open(pdf_path, "wb") as f:
            f.write(corrupted_pdf.encode("utf-8"))
