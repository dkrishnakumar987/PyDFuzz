import abc
import os
import uuid
import random
import string
from pdfrw import PdfWriter, PdfDict, PdfName


class BasePDFGenerator(abc.ABC):
    """
    Abstract base class for generating (and optionally corrupting) PDF files for fuzzing.

    Initializes common directories:
      - input_pdfs: Directory for base/seed PDF files.
      - generated_pdfs: Directory for saving generated PDF outputs.
    """

    def __init__(self):
        # Locate the project root (assumed to be two levels above this file)
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )
        # Initialize input directory for seed PDFs
        self.input_dir = os.path.join(project_root, "input_pdfs")
        os.makedirs(self.input_dir, exist_ok=True)
        # Initialize output directory for generated PDFs
        self.output_dir = os.path.join(project_root, "generated_pdfs")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf(self) -> str:
        """
        Generate a random PDF file using pdfrw and random modules and directly save it to disk.
        Each page is filled with random characters.

        The PDF will consist of a random number of pages (between 10 and 50).

        Returns:
            str: The file path of the saved PDF.
        """
        writer = PdfWriter()
        num_pages = random.randint(10, 50)
        for _ in range(num_pages):
            # Create random text of 100 characters.
            random_text = "".join(
                random.choices(
                    string.ascii_letters + string.digits + string.punctuation + " ",
                    k=100,
                )
            )
            # Build a content stream that writes the random text.
            content_str = f"BT\n/F1 24 Tf\n100 700 Td\n({random_text}) Tj\nET"
            content_stream = PdfDict(stream=content_str)
            # Create a page with A4 dimensions and add the content stream with a font resource.
            page = PdfDict(
                Type="/Page",
                MediaBox=[0, 0, 612, 792],
                Contents=content_stream,
                Resources=PdfDict(
                    Font=PdfDict(
                        F1=PdfDict(
                            BaseFont=PdfName.Helvetica,
                            Type=PdfName.Font,
                            Subtype=PdfName.Type1,
                        )
                    )
                ),
            )
            writer.addpage(page)

        # Generate a unique filename.
        filename = f"fuzzed_{uuid.uuid4().hex}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        # Write the PDF directly to disk.
        writer.write(output_path, trailer=PdfDict())
        return output_path

    @abc.abstractmethod
    def corrupt_pdf(self, pdf_path: str) -> None:
        """
        Abstract method to corrupt the given PDF file on disk.

        Args:
            pdf_path (str): The file path of the PDF to be corrupted.
        """
        pass
