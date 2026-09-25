"""Unit tests for leave approver authorization."""

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


class TestLeaveApproval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_frappe = sys.modules.get("frappe")
        cls.original_frappe_utils = sys.modules.get("frappe.utils")

        cls.frappe = types.ModuleType("frappe")
        cls.frappe._ = lambda message: message
        cls.frappe.PermissionError = TestPermissionError
        cls.frappe.session = SimpleNamespace(
            user="approver@example.com"
        )

        cls.frappe.db = SimpleNamespace(
            get_value=Mock()
        )
        cls.frappe.get_doc = Mock()
        cls.frappe.get_all = Mock()
        cls.frappe.clear_messages = Mock()

        def throw(message, exception=None):
            error = exception or TestValidationError
            raise error(message)

        def whitelist(*args, **kwargs):
            def decorator(function):
                return function

            return decorator

        cls.frappe.throw = throw
        cls.frappe.whitelist = whitelist

        frappe_utils = types.ModuleType("frappe.utils")
        frappe_utils.formatdate = lambda value: str(value)

        sys.modules["frappe"] = cls.frappe
        sys.modules["frappe.utils"] = frappe_utils
        sys.modules.pop(
            "frappe_hr_self_service.leave_approval",
            None,
        )

        cls.leave_approval = importlib.import_module(
            "frappe_hr_self_service.leave_approval"
        )

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop(
            "frappe_hr_self_service.leave_approval",
            None,
        )

        if cls.original_frappe is None:
            sys.modules.pop("frappe", None)
        else:
            sys.modules["frappe"] = cls.original_frappe

        if cls.original_frappe_utils is None:
            sys.modules.pop("frappe.utils", None)
        else:
            sys.modules["frappe.utils"] = cls.original_frappe_utils

    def setUp(self):
        self.frappe.session.user = "approver@example.com"

        self.frappe.db.get_value.reset_mock()
        self.frappe.get_doc.reset_mock()

    def leave(
        self,
        *,
        leave_approver="approver@example.com",
        docstatus=0,
        status="Open",
    ):
        return SimpleNamespace(
            name="HR-LAP-00001",
            leave_approver=leave_approver,
            docstatus=docstatus,
            status=status,
        )

    def test_guest_is_rejected_before_lookup(self):
        self.frappe.session.user = "Guest"

        with self.assertRaises(TestPermissionError):
            self.leave_approval._get_leave_for_approver(
                "HR-LAP-00001"
            )

        self.frappe.db.get_value.assert_not_called()
        self.frappe.get_doc.assert_not_called()

    def test_unassigned_request_is_rejected_without_loading_document(self):
        self.frappe.db.get_value.return_value = None

        with self.assertRaises(TestPermissionError):
            self.leave_approval._get_leave_for_approver(
                "HR-LAP-00001"
            )

        self.frappe.get_doc.assert_not_called()

    def test_authorized_request_is_returned(self):
        leave = self.leave()

        self.frappe.db.get_value.return_value = "HR-LAP-00001"
        self.frappe.get_doc.return_value = leave

        result = self.leave_approval._get_leave_for_approver(
            "HR-LAP-00001"
        )

        self.assertIs(result, leave)

        self.frappe.db.get_value.assert_called_once_with(
            "Leave Application",
            {
                "name": "HR-LAP-00001",
                "leave_approver": "approver@example.com",
            },
            "name",
        )

    def test_approver_is_rechecked_after_document_load(self):
        self.frappe.db.get_value.return_value = "HR-LAP-00001"
        self.frappe.get_doc.return_value = self.leave(
            leave_approver="other@example.com"
        )

        with self.assertRaises(TestPermissionError):
            self.leave_approval._get_leave_for_approver(
                "HR-LAP-00001"
            )

    def test_processed_request_is_rejected_when_open_required(self):
        self.frappe.db.get_value.return_value = "HR-LAP-00001"
        self.frappe.get_doc.return_value = self.leave(
            docstatus=1,
            status="Approved",
        )

        with self.assertRaises(TestValidationError):
            self.leave_approval._get_leave_for_approver(
                "HR-LAP-00001",
                require_open=True,
            )

    def test_non_open_request_is_rejected_when_open_required(self):
        self.frappe.db.get_value.return_value = "HR-LAP-00001"
        self.frappe.get_doc.return_value = self.leave(
            docstatus=0,
            status="Rejected",
        )

        with self.assertRaises(TestValidationError):
            self.leave_approval._get_leave_for_approver(
                "HR-LAP-00001",
                require_open=True,
            )
