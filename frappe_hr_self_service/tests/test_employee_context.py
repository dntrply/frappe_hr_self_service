"""Unit tests for current-user Employee resolution."""

import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import Mock


class TestValidationError(Exception):
    """Validation error raised by the fake Frappe runtime."""


class TestPermissionError(Exception):
    """Permission error raised by the fake Frappe runtime."""


class TestEmployeeContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_frappe = sys.modules.get("frappe")

        cls.frappe = types.ModuleType("frappe")
        cls.frappe._ = lambda message: message
        cls.frappe.PermissionError = TestPermissionError
        cls.frappe.session = SimpleNamespace(
            user="employee@example.com"
        )
        cls.frappe.get_all = Mock()

        def throw(message, exception=None):
            error = exception or TestValidationError
            raise error(message)

        cls.frappe.throw = throw

        sys.modules["frappe"] = cls.frappe
        sys.modules.pop(
            "frappe_hr_self_service.employee_context",
            None,
        )

        cls.employee_context = importlib.import_module(
            "frappe_hr_self_service.employee_context"
        )

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop(
            "frappe_hr_self_service.employee_context",
            None,
        )

        if cls.original_frappe is None:
            sys.modules.pop("frappe", None)
        else:
            sys.modules["frappe"] = cls.original_frappe

    def setUp(self):
        self.frappe.session.user = "employee@example.com"
        self.frappe.get_all.reset_mock()

    def employee(
        self,
        *,
        name="HR-EMP-00001",
        company="Example Company",
        leave_approver="approver@example.com",
        date_of_joining="2026-01-01",
    ):
        return SimpleNamespace(
            name=name,
            company=company,
            leave_approver=leave_approver,
            date_of_joining=date_of_joining,
        )

    def test_guest_is_rejected(self):
        self.frappe.session.user = "Guest"

        with self.assertRaises(TestPermissionError):
            self.employee_context.get_current_employee()

        self.frappe.get_all.assert_not_called()

    def test_no_active_employee_is_rejected(self):
        self.frappe.get_all.return_value = []

        with self.assertRaises(TestValidationError):
            self.employee_context.get_current_employee()

    def test_multiple_active_employees_are_rejected(self):
        self.frappe.get_all.return_value = [
            self.employee(name="HR-EMP-00001"),
            self.employee(name="HR-EMP-00002"),
        ]

        with self.assertRaises(TestValidationError):
            self.employee_context.get_current_employee()

    def test_single_active_employee_is_returned(self):
        employee = self.employee()
        self.frappe.get_all.return_value = [employee]

        result = self.employee_context.get_current_employee()

        self.assertIs(result, employee)

        self.frappe.get_all.assert_called_once_with(
            "Employee",
            filters={
                "user_id": "employee@example.com",
                "status": "Active",
            },
            fields=[
                "name",
                "company",
                "leave_approver",
                "date_of_joining",
            ],
            limit_page_length=2,
        )

    def test_company_can_be_required(self):
        self.frappe.get_all.return_value = [
            self.employee(company=None)
        ]

        with self.assertRaises(TestValidationError):
            self.employee_context.get_current_employee(
                require_company=True
            )

    def test_leave_approver_can_be_required(self):
        self.frappe.get_all.return_value = [
            self.employee(leave_approver=None)
        ]

        with self.assertRaises(TestValidationError):
            self.employee_context.get_current_employee(
                require_leave_approver=True
            )
