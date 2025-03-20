import argparse
import sys
import os
import json

from pydfuzz.fuzzing_manager import run_fuzzer
from pydfuzz.crash_handler import CrashHandler
from pydfuzz.logger import logger


def main():
    parser = argparse.ArgumentParser(description="PyDFuzz - PDF Fuzzing Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Fuzzing command
    fuzz_parser = subparsers.add_parser("fuzz", help="Generate fuzzed PDF files")
    fuzz_parser.add_argument(
        "--input", help="Optional input file for fuzzing", default=""
    )
    fuzz_parser.add_argument(
        "--generator",
        help="PDF generator to use (font, javascript, stream, xref, random)",
        default="random",
        choices=["font", "javascript", "stream", "xref", "random"],
    )

    # Crash analysis command
    crash_parser = subparsers.add_parser(
        "analyze", help="Analyze AFL++ fuzzing crashes"
    )
    crash_parser.add_argument(
        "-o",
        "--output-dir",
        default=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "output_crashes",
        ),
        help="Path to AFL++ output directory",
    )
    crash_parser.add_argument(
        "--json", action="store_true", help="Output summary as JSON instead of text"
    )

    args = parser.parse_args()

    # If no command provided, show help
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle fuzz command
    if args.command == "fuzz":
        try:
            pdf_path = run_fuzzer(args.input, args.generator)
            logger.info(f"Successfully fuzzed PDF: {pdf_path}")
        except Exception as e:
            logger.exception(f"Fuzzing session failed: {e}")
            sys.exit(f"Fuzzing session failed: {e}")

    # Handle analyze command
    elif args.command == "analyze":
        try:
            handler = CrashHandler(args.output_dir)

            if args.json:
                print(json.dumps(handler.summarize(), indent=2))
            else:
                handler.display_summary()

        except Exception as e:
            logger.error(f"Error analyzing crashes: {e}")
            sys.exit(f"Error analyzing crashes: {e}")


if __name__ == "__main__":
    main()
