#!/usr/bin/env python3
import sys
import os
import datetime
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.recurrence_run import calculate_rolling_window

class TestRecurrenceWindow(unittest.TestCase):
    def test_spec_example_august_2026(self):
        # Spec Mandate 1 Example: Run on 15 August 2026 -> 1 July 2025 to 31 July 2026 (13 full calendar months)
        ref_date = datetime.date(2026, 8, 15)
        start_date, end_date = calculate_rolling_window(ref_date)
        self.assertEqual(start_date, "2025-07-01")
        self.assertEqual(end_date, "2026-07-31")

    def test_january_execution(self):
        # Run on 10 January 2027 -> 1 December 2025 to 31 December 2026 (13 full calendar months)
        ref_date = datetime.date(2027, 1, 10)
        start_date, end_date = calculate_rolling_window(ref_date)
        self.assertEqual(start_date, "2025-12-01")
        self.assertEqual(end_date, "2026-12-31")

if __name__ == '__main__':
    unittest.main()
