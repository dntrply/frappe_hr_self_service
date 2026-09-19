"""Helpers for resolving the logged-in Frappe user to an Employee."""

import frappe
from frappe import _


def get_current_employee(
    *,
    require_company=False,
    require_leave_approver=False,
):
    """Return the single active Employee linked to the logged-in user.

    Employee identity is always derived server-side from the current
    Frappe session. A user must have exactly one active Employee record.
    """

    if frappe.session.user == "Guest":
        frappe.throw(
            _("You must be logged in."),
            frappe.PermissionError,
        )

    employees = frappe.get_all(
        "Employee",
        filters={
            "user_id": frappe.session.user,
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

    if not employees:
        frappe.throw(
            _(
                "No active Employee record is linked to your "
                "user account. Please contact HR."
            )
        )

    if len(employees) > 1:
        frappe.throw(
            _(
                "More than one active Employee record is linked "
                "to your user account. Please contact HR."
            )
        )

    employee = employees[0]

    if require_company and not employee.company:
        frappe.throw(
            _(
                "No Company is configured for your Employee "
                "record. Please contact HR."
            )
        )

    if require_leave_approver and not employee.leave_approver:
        frappe.throw(
            _(
                "No Leave Approver is configured for your "
                "Employee record. Please contact HR."
            )
        )

    return employee
