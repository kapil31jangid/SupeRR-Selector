#!/usr/bin/env python3
"""
Test runner for PRESSURE-X 2.0 regression suite.
"""

import subprocess
import sys

if __name__ == "__main__":
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/regression_test_suite.py",
        "-v",
        "--tb=short",
        "-x"
    ], capture_output=False)

    sys.exit(result.returncode)