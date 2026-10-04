"""Unit tests for the HRMS compatibility boundary."""

import importlib
import sys
import types
import unittest
from datetime import date
from unittest.mock import Mock


class TestHRMSCompat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_modules = {
            name: sys.modules.get(name)
            for name in [
                "frappe",
                "frappe.utils",
                "hrms",
                "hrms.hr",
                "hrms.hr.doctype",
                "hrms.hr.doctype.leave_application",
                "hrms.hr.doctype.leave_application.leave_application",
                "frappe_hr_self_service.hrms_compat",
            ]
        }

        frappe = types.ModuleType("frappe")
        frappe.get_all = Mock()
        frappe.db = Mock()

        frappe_utils = types.ModuleType("frappe.utils")

        def getdate(value=None):
            if value is None:
                return date.today()
            if isinstance(value, date):
                return value
            return date.fromisoformat(str(value))

        frappe_utils.getdate = getdate
        frappe_utils.cint = lambda value: int(value or 0)
        frappe_utils.flt = lambda value: float(value or 0)

        leave_application = types.ModuleType(
            "hrms.hr.doctype.leave_application.leave_application"
        )

        cls.get_number_of_leave_days = Mock(return_value=1.0)
        leave_application.get_number_of_leave_days = (
            cls.get_number_of_leave_days
        )

        for name in [
            "hrms",
            "hrms.hr",
            "hrms.hr.doctype",
            "hrms.hr.doctype.leave_application",
        ]:
            sys.modules[name] = types.ModuleType(name)

        sys.modules["frappe"] = frappe
        sys.modules["frappe.utils"] = frappe_utils
        sys.modules[
            "hrms.hr.doctype.leave_application.leave_application"
        ] = leave_application

        sys.modules.pop(
            "frappe_hr_self_service.hrms_compat",
            None,
        )

        cls.hrms_compat = importlib.import_module(
            "frappe_hr_self_service.hrms_compat"
        )

    @classmethod
    def tearDownClass(cls):
        for name, module in cls.original_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module

    def setUp(self):
        self.get_number_of_leave_days.reset_mock()
        self.get_number_of_leave_days.return_value = 1.0

    def test_requested_leave_days_preserves_full_day_behavior(self):
        result = self.hrms_compat.get_requested_leave_days(
            "HR-EMP-00001",
            "Example Leave",
            "2026-10-15",
            "2026-10-15",
        )

        self.assertEqual(result, 1.0)

        self.get_number_of_leave_days.assert_called_once_with(
            "HR-EMP-00001",
            "Example Leave",
            date(2026, 10, 15),
            date(2026, 10, 15),
            half_day=0,
            half_day_date=None,
        )

    def test_requested_leave_days_passes_half_day_values(self):
        self.get_number_of_leave_days.return_value = 0.5

        result = self.hrms_compat.get_requested_leave_days(
            "HR-EMP-00001",
            "Example Leave",
            "2026-10-15",
            "2026-10-15",
            half_day=1,
            half_day_date="2026-10-15",
        )

        self.assertEqual(result, 0.5)

        self.get_number_of_leave_days.assert_called_once_with(
            "HR-EMP-00001",
            "Example Leave",
            date(2026, 10, 15),
            date(2026, 10, 15),
            half_day=1,
            half_day_date=date(2026, 10, 15),
        )


if __name__ == "__main__":
    unittest.main()
