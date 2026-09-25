"""Employee-facing leave self-service API."""

import frappe
from frappe import _
from frappe.utils import date_diff, flt, getdate

from frappe_hr_self_service.employee_context import get_current_employee
from frappe_hr_self_service.hrms_compat import (
    get_allocated_leave_types,
    get_consumable_leave_balance,
    get_leave_balance_map,
    get_leave_type_rules,
    get_overlapping_leave_application,
    get_requested_leave_days,
)


@frappe.whitelist()
def get_my_leave_balance():
    """Return normalized leave balances for the logged-in employee."""

    employee = get_current_employee()

    return get_leave_balance_map(employee.name)


@frappe.whitelist()
def get_available_leave_types(from_date=None, to_date=None):
    """Return leave-type eligibility for the logged-in employee.

    This endpoint is a preflight aid for employee self-service. Native HRMS
    validation remains authoritative when a Leave Application is created.
    """

    employee = get_current_employee()

    if not from_date or not to_date:
        return {"leave_types": []}

    from_date = getdate(from_date)
    to_date = getdate(to_date)

    if to_date < from_date:
        frappe.throw(_("To Date cannot be before From Date."))

    existing_request = get_overlapping_leave_application(
        employee.name,
        from_date,
        to_date,
    )

    if existing_request:
        return {
            "from_date": str(from_date),
            "to_date": str(to_date),
            "existing_request": existing_request,
            "leave_types": [],
        }

    leave_types = get_allocated_leave_types(
        employee.name,
        from_date,
        to_date,
    )

    results = []

    for leave_type in leave_types:
        settings = get_leave_type_rules(leave_type)

        requested_days = get_requested_leave_days(
            employee.name,
            leave_type,
            from_date,
            to_date,
        )

        balances = get_consumable_leave_balance(
            employee.name,
            leave_type,
            from_date,
            to_date,
        )

        balance = balances["leave_balance"]
        consumable = balances["leave_balance_for_consumption"]

        eligible = True
        reason = None

        if requested_days <= 0:
            eligible = False
            reason = _(
                "The selected dates are holidays for this leave type."
            )

        applicable_after = int(
            settings.get("applicable_after") or 0
        )

        if eligible and applicable_after > 0:
            if not employee.date_of_joining:
                eligible = False
                reason = _(
                    "Your Date of Joining is not configured. "
                    "Please contact HR."
                )
            elif (
                date_diff(from_date, employee.date_of_joining)
                < applicable_after
            ):
                eligible = False
                reason = _(
                    "This leave type becomes available after "
                    "{0} calendar days of service."
                ).format(applicable_after)

        allow_negative = bool(
            settings.get("allow_negative")
        )

        if eligible and not allow_negative:
            if consumable <= 0:
                eligible = False
                reason = _(
                    "No leave balance remains for this leave type."
                )
            elif consumable < requested_days:
                eligible = False
                reason = _(
                    "{0} leave days are required, but only "
                    "{1} are available."
                ).format(
                    requested_days,
                    consumable,
                )

        results.append(
            {
                "leave_type": leave_type,
                "requested_days": requested_days,
                "balance": balance,
                "available_for_request": consumable,
                "eligible": eligible,
                "reason": reason,
            }
        )

    return {
        "from_date": str(from_date),
        "to_date": str(to_date),
        "existing_request": None,
        "leave_types": results,
    }


def _create_leave_application(
    *,
    leave_type,
    from_date,
    to_date,
    reason=None,
):
    """Create a Leave Application for the logged-in employee."""

    employee = get_current_employee(
        require_company=True,
        require_leave_approver=True,
    )

    doc = frappe.get_doc(
        {
            "doctype": "Leave Application",
            "employee": employee.name,
            "company": employee.company,
            "leave_approver": employee.leave_approver,
            "leave_type": leave_type,
            "from_date": getdate(from_date),
            "to_date": getdate(to_date),
            "description": reason or "",
            "status": "Open",
            "follow_via_email": 1,
        }
    )

    doc.insert(ignore_permissions=True)

    return doc


@frappe.whitelist(methods=["POST"])
def create_leave_request(
    from_date=None,
    to_date=None,
    leave_type=None,
    reason=None,
):
    """Create a leave request after server-side eligibility checks."""

    # Establish employee context before accepting the request payload.
    get_current_employee(
        require_company=True,
        require_leave_approver=True,
    )

    if not from_date or not to_date:
        frappe.throw(_("From Date and To Date are required."))

    if not leave_type:
        frappe.throw(_("Please select a Leave Type."))

    from_date = getdate(from_date)
    to_date = getdate(to_date)

    if to_date < from_date:
        frappe.throw(_("To Date cannot be before From Date."))

    # Re-evaluate eligibility at submission time.
    # Never trust a Leave Type merely because the browser offered it.
    availability = get_available_leave_types(
        from_date=from_date,
        to_date=to_date,
    )

    if availability.get("existing_request"):
        frappe.throw(
            _(
                "You already have a leave request "
                "covering these dates."
            )
        )

    selected = next(
        (
            row
            for row in availability["leave_types"]
            if row["leave_type"] == leave_type
        ),
        None,
    )

    if not selected:
        frappe.throw(
            _(
                "The selected leave type is not available "
                "for these dates."
            )
        )

    if not selected["eligible"]:
        frappe.throw(
            selected["reason"]
            or _(
                "The selected leave type cannot be used "
                "for these dates."
            )
        )

    doc = _create_leave_application(
        leave_type=leave_type,
        from_date=from_date,
        to_date=to_date,
        reason=reason,
    )

    # Avoid carrying incidental HRMS notification messages into
    # the simplified self-service response.
    frappe.clear_messages()

    return {
        "name": doc.name,
        "status": doc.status,
        "leave_type": doc.leave_type,
        "from_date": str(doc.from_date),
        "to_date": str(doc.to_date),
        "total_leave_days": flt(doc.total_leave_days),
    }
