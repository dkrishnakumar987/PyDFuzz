import random
from pydfuzz.pdf_generator.base_generator import BasePDFGenerator


class CorruptXrefPDFGenerator(BasePDFGenerator):
    """
    Generates a PDF file with a corrupted xref table.
    Inherits PDF generation from BasePDFGenerator and corrupts its XREF table.
    """

    def corrupt_pdf(self, pdf_path: str) -> None:
        """
        Open the PDF at pdf_path, corrupt its XREF table by altering the startxref value,
        and write the corrupted PDF back to disk.

        Args:
            pdf_path (str): The file path of the PDF to be corrupted.
        """
        # Read the current PDF content.
        with open(pdf_path, "rb") as f:
            content = f.read().decode("utf-8", errors="ignore")

        # Split the content into lines.
        lines = content.splitlines()
        try:
            # Locate the "startxref" marker.
            idx = lines.index("startxref")
            # Replace the next line (which should be a numeric value) with a corruption.
            lines[idx + 1] = random.choice(["CORRUPT", f"{random.randint(1, 10000)}"])
        except (ValueError, IndexError):
            # If "startxref" is not found, append a corrupted startxref section.
            lines.extend(
                [
                    "startxref",
                    random.choice(["CORRUPT", f"{random.randint(1, 10000)}"]),
                    "%%EOF",
                ]
            )

        # Reassemble content and write back to disk.
        corrupted_content = "\n".join(lines)
        with open(pdf_path, "wb") as f:
            f.write(corrupted_content.encode("utf-8"))
