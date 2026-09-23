"""
Standalone QA Test Runner for Sprint 1 Deliverables (SOMOS Internet)
"""
import sys
import pytest

if __name__ == "__main__":
    print("=====================================================================")
    print("STARTING QA TEST SUITE EXECUTION VIA PYTEST")
    print("=====================================================================")
    exit_code = pytest.main(["-v", "-s", "test_sprint1_deliverables.py"])
    sys.exit(exit_code)
