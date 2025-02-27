import argparse
import sys
from pydfuzz.fuzzing_manager import run_fuzzer
from pydfuzz.logger import logger


def main():
    parser = argparse.ArgumentParser(description="MuPDF Fuzzing Manager")
    parser.add_argument("--input", help="Optional input file for fuzzing", default="")
    parser.add_argument(
        "--generator",
        help="PDF generator to use (font, javascript, stream, xref, random)",
        default="random",
        choices=["font", "javascript", "stream", "xref", "random"],
    )
    args = parser.parse_args()

    try:
        pdf_path = run_fuzzer(args.input, args.generator)
        logger.info(f"Successfully fuzzed PDF: {pdf_path}")
    except Exception as e:
        logger.exception(f"Fuzzing session failed: {e}")
        sys.exit(f"Fuzzing session failed: {e}")


if __name__ == "__main__":
    main()
