from pydfuzz.pdf_generator.base_generator import BasePDFGenerator


class CorruptJavaScriptPDFGenerator(BasePDFGenerator):
    """
    Generates a PDF file and then corrupts it by injecting a JavaScript action
    designed to crash PDF readers. This implementation injects a new PDF object
    containing an enormous JavaScript payload and appends it before the trailer.
    """

    def corrupt_pdf(self, pdf_path: str) -> None:
        """
        Opens the PDF at pdf_path, injects a JavaScript object with a malicious payload,
        and writes the modified PDF back to disk.

        Args:
            pdf_path (str): The file path of the PDF to be corrupted.
        """
        # Read the original PDF content.
        with open(pdf_path, "rb") as f:
            content = f.read().decode("utf-8", errors="ignore")

        # Create a malicious JavaScript payload.
        # Repeating a loop construct many times to overwhelm the PDF reader.
        malicious_js = "while(true){};" * 1000

        # Build a new PDF object (object number "100 0 obj") containing the JavaScript action.
        js_object = (
            "100 0 obj\n"
            "<< /Type /Action /S /JavaScript /JS (" + malicious_js + ") >>\n"
            "endobj\n"
        )

        # Inject the new JS object before the "trailer" section.
        if "trailer" in content:
            parts = content.split("trailer", 1)
            new_content = parts[0] + js_object + "\ntrailer" + parts[1]
        else:
            # If no trailer is found, simply append the object at the end.
            new_content = content + js_object

        # Write the modified PDF content back to disk.
        with open(pdf_path, "wb") as f:
            f.write(new_content.encode("utf-8"))
