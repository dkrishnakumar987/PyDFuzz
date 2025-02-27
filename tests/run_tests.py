import unittest


def main():
    # Discover and run tests in the "tests" directory
    tests = unittest.TestLoader().discover(start_dir="tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(tests)
    # Return an exit code based on test results.
    exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
