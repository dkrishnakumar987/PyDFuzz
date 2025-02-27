import random
from typing import List, Type

from pydfuzz.logger import logger
from pydfuzz.pdf_generator.base_generator import BasePDFGenerator
from pydfuzz.pdf_generator.corrupt_font import CorruptFontPDFGenerator
from pydfuzz.pdf_generator.corrupt_javascript import CorruptJavaScriptPDFGenerator
from pydfuzz.pdf_generator.corrupt_stream import CorruptStreamPDFGenerator
from pydfuzz.pdf_generator.corrupt_xref import CorruptXrefPDFGenerator

# Import once fuzz_executor and crash_handler are implemented
# from pydfuzz.fuzz_executor import FuzzExecutor
# from pydfuzz.crash_handler import CrashHandler


def get_available_generators() -> List[Type[BasePDFGenerator]]:
    """Returns a list of available PDF generator classes"""
    return [
        CorruptFontPDFGenerator,
        CorruptJavaScriptPDFGenerator,
        CorruptStreamPDFGenerator,
        CorruptXrefPDFGenerator,
    ]


def run_fuzzer(input_file: str = "", generator_name: str = "random"):
    """
    Run the PDF fuzzer with the specified generator or a random one

    Args:
        input_file: Optional input PDF file path to use as base
        generator_name: Name of the generator to use ('font', 'javascript', 'stream', 'xref' or 'random')
    """
    logger.debug(f"Starting MuPDF fuzzing session with generator: {generator_name}")

    # Map generator names to their respective classes
    generator_map = {
        "font": CorruptFontPDFGenerator,
        "javascript": CorruptJavaScriptPDFGenerator,
        "stream": CorruptStreamPDFGenerator,
        "xref": CorruptXrefPDFGenerator,
        "random": None,  # Will be selected randomly
    }

    # Select the generator class
    if generator_name == "random":
        generator_class = random.choice(get_available_generators())
        logger.info(f"Randomly selected generator: {generator_class.__name__}")
    else:
        if generator_name not in generator_map:
            logger.error(f"Invalid generator name: {generator_name}")
            return
        generator_class = generator_map[generator_name]

    # Create the generator instance
    generator = generator_class()

    # Generate a fuzzed PDF
    logger.info("Generating PDF...")
    pdf_path = generator.generate_pdf()
    logger.info(f"Generated PDF at: {pdf_path}")

    # Corrupt the PDF
    logger.info("Corrupting PDF...")
    generator.corrupt_pdf(pdf_path)
    logger.info(f"PDF corrupted with {generator_class.__name__}")

    # Once implemented, execute the fuzzing using FuzzExecutor
    # executor = FuzzExecutor()
    # result = executor.run(pdf_path)

    # Once implemented, check and process any crash encountered during fuzzing
    # crash_handler = CrashHandler()
    # if crash_handler.detect(result):
    #     crash_handler.handle(result)
    #     logger.error("Crash detected during fuzzing.")

    logger.debug("Fuzzing session completed.")
    return pdf_path
