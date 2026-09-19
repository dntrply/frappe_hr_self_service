"""Approver-facing leave self-service API."""

import frappe
from frappe import _
from frappe.utils import formatdate


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
        "total_leave_days": leave.total_leave_days,
        "reason": leave.description or "",
        "status": leave.status,
        "docstatus": leave.docstatus,
    }
