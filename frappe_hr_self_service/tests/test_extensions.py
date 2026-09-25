"""Unit tests for organization-specific leave eligibility extensions."""

import importlib
import sys
import types
import unittest
from datetime import date
from unittest.mock import Mock


class TestLeaveEligibilityExtensions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_frappe = sys.modules.get("frappe")

        cls.frappe = types.ModuleType("frappe")
        cls.frappe.get_hooks = Mock()
        cls.frappe.get_attr = Mock()

        sys.modules["frappe"] = cls.frappe
        sys.modules.pop(
            "frappe_hr_self_service.extensions",
            None,
        )

        cls.extensions = importlib.import_module(
            "frappe_hr_self_service.extensions"
        )

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop(
            "frappe_hr_self_service.extensions",
            None,
        )

        if cls.original_frappe is None:
            sys.modules.pop("frappe", None)
        else:
            sys.modules["frappe"] = cls.original_frappe

    def setUp(self):
        self.frappe.get_hooks.reset_mock()
        self.frappe.get_attr.reset_mock()

    def call_extension(self):
        return (
            self.extensions
            .get_leave_eligibility_extension_reason(
                employee="HR-EMP-00001",
                company="Example Company",
                leave_type="Example Leave",
                from_date=date(2026, 9, 20),
                to_date=date(2026, 9, 21),
                requested_days=2.0,
                balance=5.0,
                available_for_request=5.0,
            )
        )

    def test_no_extensions_returns_none(self):
        self.frappe.get_hooks.return_value = []

        result = self.call_extension()

        self.assertIsNone(result)

        self.frappe.get_hooks.assert_called_once_with(
            "frappe_hr_self_service_leave_eligibility"
        )
        self.frappe.get_attr.assert_not_called()

    def test_empty_extension_result_does_not_block(self):
        callback = Mock(return_value=None)

        self.frappe.get_hooks.return_value = [
            "example_app.leave_rules.check_leave"
        ]
        self.frappe.get_attr.return_value = callback

        result = self.call_extension()

        self.assertIsNone(result)

        callback.assert_called_once_with(
            employee="HR-EMP-00001",
            company="Example Company",
            leave_type="Example Leave",
            from_date=date(2026, 9, 20),
            to_date=date(2026, 9, 21),
            requested_days=2.0,
            balance=5.0,
            available_for_request=5.0,
        )

    def test_first_blocking_reason_is_returned(self):
        first = Mock(return_value="Organization rule blocks this leave.")
        second = Mock(return_value="Second reason")

        self.frappe.get_hooks.return_value = [
            "example_app.leave_rules.first",
            "example_app.leave_rules.second",
        ]

        self.frappe.get_attr.side_effect = {
            "example_app.leave_rules.first": first,
            "example_app.leave_rules.second": second,
        }.__getitem__

        result = self.call_extension()

        self.assertEqual(
            result,
            "Organization rule blocks this leave.",
        )
        first.assert_called_once()
        second.assert_not_called()

    def test_later_extension_can_block(self):
        first = Mock(return_value=None)
        second = Mock(return_value="Second extension blocks leave.")

        self.frappe.get_hooks.return_value = [
            "example_app.leave_rules.first",
            "example_app.leave_rules.second",
        ]

        self.frappe.get_attr.side_effect = {
            "example_app.leave_rules.first": first,
            "example_app.leave_rules.second": second,
        }.__getitem__

        result = self.call_extension()

        self.assertEqual(
            result,
            "Second extension blocks leave.",
        )
        first.assert_called_once()
        second.assert_called_once()
