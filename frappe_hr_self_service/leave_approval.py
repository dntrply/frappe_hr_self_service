"""Approver-facing leave self-service API."""

import frappe
from frappe import _
from frappe.utils import cint, formatdate


REJECTION_REASON_FIELD = "custom_rejection_reason"


def _get_leave_for_approver(name, require_open=False):
    """Return a Leave Application only when the current user is its approver."""

    if frappe.session.user == "Guest":
        frappe.throw(
            _("Please log in."),
            frappe.PermissionError,
        )

    if not name:
        frappe.throw(_("Leave Application is required."))

    authorized_name = frappe.db.get_value(
        "Leave Application",
        {
            "name": name,
            "leave_approver": frappe.session.user,
        },
        "name",
    )

    if not authorized_name:
        frappe.throw(
            _("Leave request not found or not assigned to you."),
            frappe.PermissionError,
        )

    leave = frappe.get_doc(
        "Leave Application",
        authorized_name,
    )

    # The designated Leave Approver is the primary self-service
    # authorization boundary.
    if leave.leave_approver != frappe.session.user:
        frappe.throw(
            _("You are not the approver for this leave request."),
            frappe.PermissionError,
        )

    if require_open:
        if leave.docstatus != 0:
            frappe.throw(
                _("This leave request has already been processed.")
            )

        if leave.status != "Open":
            frappe.throw(
                _(
                    "This leave request is no longer open. "
                    "Current status: {0}"
                ).format(leave.status)
            )

    return leave


def _normalize_rejection_reason(reason):
    """Return a trimmed rejection reason or raise when it is empty."""

    reason = str(reason or "").strip()

    if not reason:
        frappe.throw(
            _("Please provide a reason for rejecting this leave request.")
        )

    return reason


def validate_rejection_reason(doc, method=None):
    """Require a reason before a rejected Leave Application is submitted."""

    if doc.status != "Rejected":
        return

    reason = _normalize_rejection_reason(
        getattr(doc, REJECTION_REASON_FIELD, None)
    )
    setattr(doc, REJECTION_REASON_FIELD, reason)


@frappe.whitelist()
def get_pending_leave_approvals():
    """Return open leave requests assigned to the logged-in approver."""

    if frappe.session.user == "Guest":
        frappe.throw(
            _("Please log in."),
            frappe.PermissionError,
        )

    rows = frappe.get_all(
        "Leave Application",
        filters={
            "leave_approver": frappe.session.user,
            "status": "Open",
            "docstatus": 0,
        },
        fields=[
            "name",
            "employee_name",
            "leave_type",
            "from_date",
            "to_date",
            "half_day",
            "half_day_date",
            "total_leave_days",
            "description",
        ],
        order_by="from_date asc, creation asc",
    )

    return [
        {
            "name": row.name,
            "employee_name": row.employee_name,
            "leave_type": row.leave_type,
            "from_date": formatdate(row.from_date),
            "to_date": formatdate(row.to_date),
            "half_day": cint(row.half_day),
            "half_day_date": (
                formatdate(row.half_day_date)
                if row.half_day_date
                else None
            ),
            "total_leave_days": row.total_leave_days,
            "reason": row.description or "",
        }
        for row in rows
    ]


@frappe.whitelist()
def get_leave_for_approval(name):
    """Return one leave request when the current user is its approver."""

    leave = _get_leave_for_approver(name)

    return {
        "name": leave.name,
        "employee_name": leave.employee_name,
        "leave_type": leave.leave_type,
        "from_date": formatdate(leave.from_date),
        "to_date": formatdate(leave.to_date),
        "half_day": cint(leave.half_day),
        "half_day_date": (
            formatdate(leave.half_day_date)
            if leave.half_day_date
            else None
        ),
        "total_leave_days": leave.total_leave_days,
        "reason": leave.description or "",
        "status": leave.status,
        "docstatus": leave.docstatus,
        "rejection_reason": (
            getattr(leave, REJECTION_REASON_FIELD, None) or ""
        ),
    }


@frappe.whitelist(methods=["POST"])
def approve_leave(name):
    """Approve an open leave request assigned to the logged-in approver."""

    leave = _get_leave_for_approver(
        name,
        require_open=True,
    )

    # Preserve native HRMS permission enforcement in addition to
    # the self-service approver authorization check.
    leave.check_permission("submit")

    leave.status = "Approved"
    leave.submit()

    frappe.clear_messages()

    return {
        "name": leave.name,
        "status": leave.status,
        "docstatus": leave.docstatus,
        "message": _("Leave request approved."),
    }


@frappe.whitelist(methods=["POST"])
def reject_leave(name, reason=None):
    """Reject an open leave request with an auditable rejection reason."""

    leave = _get_leave_for_approver(
        name,
        require_open=True,
    )

    leave.check_permission("submit")

    reason = _normalize_rejection_reason(reason)
    setattr(leave, REJECTION_REASON_FIELD, reason)
    leave.status = "Rejected"
    leave.submit()

    frappe.clear_messages()

    return {
        "name": leave.name,
        "status": leave.status,
        "docstatus": leave.docstatus,
        "rejection_reason": reason,
        "message": _("Leave request rejected."),
    }
