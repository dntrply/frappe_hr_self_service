"""Unit tests for employee leave self-service."""

import importlib
import sys
import types
import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock


class TestValidationError(Exception):
    """Validation error raised by the fake Frappe runtime."""


class TestEmployeeSelfService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_modules = {
            name: sys.modules.get(name)
            for name in [
                "frappe",
                "frappe.utils",
                "frappe_hr_self_service.employee_context",
                "frappe_hr_self_service.extensions",
                "frappe_hr_self_service.hrms_compat",
                "frappe_hr_self_service.employee_self_service",
            ]
        }

        cls.frappe = types.ModuleType("frappe")
        cls.frappe._ = lambda message: message

        def throw(message, exception=None):
            error = exception or TestValidationError
            raise error(message)

        def whitelist(*args, **kwargs):
            def decorator(function):
                return function

            return decorator

        cls.frappe.throw = throw
        cls.frappe.whitelist = whitelist
        cls.frappe.get_doc = Mock()
        cls.frappe.clear_messages = Mock()

        frappe_utils = types.ModuleType("frappe.utils")

        def getdate(value=None):
            if value is None:
                return date.today()
            if isinstance(value, date):
                return value
            return date.fromisoformat(str(value))

        frappe_utils.getdate = getdate
        frappe_utils.date_diff = (
            lambda first, second:
            (getdate(first) - getdate(second)).days
        )
        frappe_utils.flt = lambda value: float(value or 0)

        cls.employee = SimpleNamespace(
            name="HR-EMP-00001",
            company="Example Company",
            leave_approver="approver@example.com",
            date_of_joining=date(2026, 1, 1),
        )

        employee_context = types.ModuleType(
            "frappe_hr_self_service.employee_context"
        )
        employee_context.get_current_employee = Mock(
            return_value=cls.employee
        )
        cls.get_current_employee = (
            employee_context.get_current_employee
        )

        extensions = types.ModuleType(
            "frappe_hr_self_service.extensions"
        )
        cls.get_leave_eligibility_extension_reason = Mock(
            return_value=None
        )
        extensions.get_leave_eligibility_extension_reason = (
            cls.get_leave_eligibility_extension_reason
        )

        hrms_compat = types.ModuleType(
            "frappe_hr_self_service.hrms_compat"
        )

        cls.get_leave_balance_map = Mock()
        cls.get_requested_leave_days = Mock()
        cls.get_consumable_leave_balance = Mock()
        cls.get_allocated_leave_types = Mock()
        cls.get_leave_type_rules = Mock()
        cls.get_overlapping_leave_application = Mock()

        hrms_compat.get_leave_balance_map = (
            cls.get_leave_balance_map
        )
        hrms_compat.get_requested_leave_days = (
            cls.get_requested_leave_days
        )
        hrms_compat.get_consumable_leave_balance = (
            cls.get_consumable_leave_balance
        )
        hrms_compat.get_allocated_leave_types = (
            cls.get_allocated_leave_types
        )
        hrms_compat.get_leave_type_rules = (
            cls.get_leave_type_rules
        )
        hrms_compat.get_overlapping_leave_application = (
            cls.get_overlapping_leave_application
        )

        sys.modules["frappe"] = cls.frappe
        sys.modules["frappe.utils"] = frappe_utils
        sys.modules[
            "frappe_hr_self_service.employee_context"
        ] = employee_context
        sys.modules[
            "frappe_hr_self_service.extensions"
        ] = extensions
        sys.modules[
            "frappe_hr_self_service.hrms_compat"
        ] = hrms_compat
        sys.modules.pop(
            "frappe_hr_self_service.employee_self_service",
            None,
        )

        cls.employee_self_service = importlib.import_module(
            "frappe_hr_self_service.employee_self_service"
        )

    @classmethod
    def tearDownClass(cls):
        for name, module in cls.original_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module

    def setUp(self):
        self.employee.date_of_joining = date(2026, 1, 1)

        for mock in [
            self.get_current_employee,
            self.get_leave_eligibility_extension_reason,
            self.get_leave_balance_map,
            self.get_requested_leave_days,
            self.get_consumable_leave_balance,
            self.get_allocated_leave_types,
            self.get_leave_type_rules,
            self.get_overlapping_leave_application,
        ]:
            mock.reset_mock()

        self.frappe.get_doc.reset_mock()
        self.frappe.get_doc.return_value = None
        self.frappe.clear_messages.reset_mock()

        self.get_current_employee.return_value = self.employee
        self.get_leave_eligibility_extension_reason.return_value = None
        self.get_overlapping_leave_application.return_value = None
        self.get_allocated_leave_types.return_value = [
            "Example Leave"
        ]
        self.get_leave_type_rules.return_value = {
            "applicable_after": 0,
            "allow_negative": False,
        }
        self.get_requested_leave_days.return_value = 1.0
        self.get_consumable_leave_balance.return_value = {
            "leave_balance": 5.0,
            "leave_balance_for_consumption": 5.0,
        }

    def test_missing_dates_still_resolve_current_employee(self):
        result = (
            self.employee_self_service.get_available_leave_types()
        )

        self.assertEqual(result, {"leave_types": []})
        self.get_current_employee.assert_called_once_with()

    def test_reversed_dates_are_rejected(self):
        with self.assertRaises(TestValidationError):
            self.employee_self_service.get_available_leave_types(
                "2026-09-20",
                "2026-09-19",
            )

    def test_overlap_short_circuits_leave_type_checks(self):
        existing = {
            "name": "HR-LAP-00001",
            "status": "Open",
        }
        self.get_overlapping_leave_application.return_value = (
            existing
        )

        result = (
            self.employee_self_service.get_available_leave_types(
                "2026-09-20",
                "2026-09-20",
            )
        )

        self.assertEqual(result["existing_request"], existing)
        self.assertEqual(result["leave_types"], [])
        self.get_allocated_leave_types.assert_not_called()

    def test_leave_type_is_eligible_with_sufficient_balance(self):
        result = (
            self.employee_self_service.get_available_leave_types(
                "2026-09-20",
                "2026-09-20",
            )
        )

        row = result["leave_types"][0]

        self.assertEqual(row["leave_type"], "Example Leave")
        self.assertTrue(row["eligible"])
        self.assertIsNone(row["reason"])
        self.assertEqual(row["requested_days"], 1.0)
        self.assertEqual(row["available_for_request"], 5.0)

    def test_applicable_after_waiting_period_is_enforced(self):
        self.employee.date_of_joining = date(2026, 9, 1)
        self.get_leave_type_rules.return_value = {
            "applicable_after": 30,
            "allow_negative": False,
        }

        result = (
            self.employee_self_service.get_available_leave_types(
                "2026-09-20",
                "2026-09-20",
            )
        )

        row = result["leave_types"][0]

        self.assertFalse(row["eligible"])
        self.assertIn(
            "30 calendar days",
            row["reason"],
        )

    def test_insufficient_balance_is_rejected(self):
        self.get_requested_leave_days.return_value = 3.0
        self.get_consumable_leave_balance.return_value = {
            "leave_balance": 2.0,
            "leave_balance_for_consumption": 2.0,
        }

        result = (
            self.employee_self_service.get_available_leave_types(
                "2026-09-20",
                "2026-09-22",
            )
        )

        row = result["leave_types"][0]

        self.assertFalse(row["eligible"])
        self.assertIn(
            "only 2.0 are available",
            row["reason"],
        )

    def test_negative_balance_leave_type_bypasses_balance_check(self):
        self.get_leave_type_rules.return_value = {
            "applicable_after": 0,
            "allow_negative": True,
        }
        self.get_requested_leave_days.return_value = 3.0
        self.get_consumable_leave_balance.return_value = {
            "leave_balance": 0.0,
            "leave_balance_for_consumption": 0.0,
        }

        result = (
            self.employee_self_service.get_available_leave_types(
                "2026-09-20",
                "2026-09-22",
            )
        )

        self.assertTrue(
            result["leave_types"][0]["eligible"]
        )

    def test_create_request_rejects_overlap_before_insert(self):
        self.get_overlapping_leave_application.return_value = {
            "name": "HR-LAP-00001",
            "status": "Open",
        }

        with self.assertRaises(TestValidationError):
            self.employee_self_service.create_leave_request(
                from_date="2026-09-20",
                to_date="2026-09-20",
                leave_type="Example Leave",
            )

        self.frappe.get_doc.assert_not_called()

    def test_create_request_rejects_unavailable_leave_type(self):
        self.get_allocated_leave_types.return_value = []

        with self.assertRaises(TestValidationError):
            self.employee_self_service.create_leave_request(
                from_date="2026-09-20",
                to_date="2026-09-20",
                leave_type="Not Allocated Leave",
            )

        self.frappe.get_doc.assert_not_called()

    def test_create_request_rejects_ineligible_leave_type(self):
        self.get_consumable_leave_balance.return_value = {
            "leave_balance": 0.0,
            "leave_balance_for_consumption": 0.0,
        }

        with self.assertRaises(TestValidationError):
            self.employee_self_service.create_leave_request(
                from_date="2026-09-20",
                to_date="2026-09-20",
                leave_type="Example Leave",
            )

        self.frappe.get_doc.assert_not_called()

    def test_create_request_uses_server_derived_employee_context(self):
        insert = Mock()
        document = SimpleNamespace(
            name="HR-LAP-00001",
            status="Open",
            leave_type="Example Leave",
            from_date=date(2026, 9, 20),
            to_date=date(2026, 9, 20),
            total_leave_days=1.0,
            insert=insert,
        )
        self.frappe.get_doc.return_value = document

        result = self.employee_self_service.create_leave_request(
            from_date="2026-09-20",
            to_date="2026-09-20",
            leave_type="Example Leave",
            reason="Family event",
        )

        self.frappe.get_doc.assert_called_once_with(
            {
                "doctype": "Leave Application",
                "employee": "HR-EMP-00001",
                "company": "Example Company",
                "leave_approver": "approver@example.com",
                "leave_type": "Example Leave",
                "from_date": date(2026, 9, 20),
                "to_date": date(2026, 9, 20),
                "description": "Family event",
                "status": "Open",
                "follow_via_email": 1,
            }
        )

        insert.assert_called_once_with(
            ignore_permissions=True
        )

        self.get_current_employee.assert_any_call(
            require_company=True,
            require_leave_approver=True,
        )

        self.frappe.clear_messages.assert_called_once_with()

        self.assertEqual(result["name"], "HR-LAP-00001")
        self.assertEqual(result["status"], "Open")
        self.assertEqual(result["leave_type"], "Example Leave")
        self.assertEqual(result["total_leave_days"], 1.0)

    def test_extension_can_block_core_eligible_leave(self):
        self.get_leave_eligibility_extension_reason.return_value = (
            "Organization policy blocks this leave."
        )

        result = (
            self.employee_self_service.get_available_leave_types(
                "2026-09-20",
                "2026-09-20",
            )
        )

        row = result["leave_types"][0]

        self.assertFalse(row["eligible"])
        self.assertEqual(
            row["reason"],
            "Organization policy blocks this leave.",
        )

        self.get_leave_eligibility_extension_reason.assert_called_once_with(
            employee="HR-EMP-00001",
            company="Example Company",
            leave_type="Example Leave",
            from_date=date(2026, 9, 20),
            to_date=date(2026, 9, 20),
            requested_days=1.0,
            balance=5.0,
            available_for_request=5.0,
        )

    def test_extension_is_not_called_after_core_rejection(self):
        self.get_consumable_leave_balance.return_value = {
            "leave_balance": 0.0,
            "leave_balance_for_consumption": 0.0,
        }

        result = (
            self.employee_self_service.get_available_leave_types(
                "2026-09-20",
                "2026-09-20",
            )
        )

        self.assertFalse(
            result["leave_types"][0]["eligible"]
        )

        self.get_leave_eligibility_extension_reason.assert_not_called()
