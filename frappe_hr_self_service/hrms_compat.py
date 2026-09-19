"""Compatibility boundary between this app and Frappe HR.

Only this module should directly import HRMS implementation helpers where
practical. If HRMS changes module paths, signatures, or return structures,
adapt them here while keeping the self-service API stable.
"""

import frappe
from frappe.utils import cint, flt, getdate


def get_leave_balance_map(employee, date=None):
    """Return a stable leave-balance structure for one employee."""

    from hrms.hr.doctype.leave_application.leave_application import (
        get_leave_details,
    )

    check_date = getdate(date) if date else getdate()

    details = get_leave_details(employee, check_date)
    allocation = details.get("leave_allocation") or {}

    return {
        leave_type: {
            "allocated_leaves": flt(values.get("total_leaves")),
            "balance_leaves": flt(values.get("remaining_leaves")),
        }
        for leave_type, values in allocation.items()
    }


def get_requested_leave_days(
    employee,
    leave_type,
    from_date,
    to_date,
):
    """Return leave days consumed for the given dates and leave type."""

    from hrms.hr.doctype.leave_application.leave_application import (
        get_number_of_leave_days,
    )

    return flt(
        get_number_of_leave_days(
            employee,
            leave_type,
            getdate(from_date),
            getdate(to_date),
        )
    )


def get_consumable_leave_balance(
    employee,
    leave_type,
    from_date,
    to_date,
):
    """Return a normalized balance structure for leave consumption."""

    from hrms.hr.doctype.leave_application.leave_application import (
        get_leave_balance_on,
    )

    result = (
        get_leave_balance_on(
            employee,
            leave_type,
            getdate(from_date),
            to_date=getdate(to_date),
            consider_all_leaves_in_the_allocation_period=True,
            for_consumption=True,
        )
        or {}
    )

    return {
        "leave_balance": flt(result.get("leave_balance")),
        "leave_balance_for_consumption": flt(
            result.get("leave_balance_for_consumption")
        ),
    }


def get_allocated_leave_types(
    employee,
    from_date,
    to_date,
):
    """Return leave types with submitted allocations covering the full period."""

    rows = frappe.get_all(
        "Leave Allocation",
        filters=[
            ["Leave Allocation", "employee", "=", employee],
            ["Leave Allocation", "docstatus", "=", 1],
            ["Leave Allocation", "from_date", "<=", getdate(from_date)],
            ["Leave Allocation", "to_date", ">=", getdate(to_date)],
        ],
        fields=["leave_type"],
    )

    return sorted(
        {
            row.leave_type
            for row in rows
            if row.leave_type
        }
    )


def get_leave_type_rules(leave_type):
    """Return normalized rules for one HRMS Leave Type."""

    values = frappe.db.get_value(
        "Leave Type",
        leave_type,
        [
            "applicable_after",
            "allow_negative",
        ],
        as_dict=True,
    ) or {}

    return {
        "applicable_after": cint(
            values.get("applicable_after")
        ),
        "allow_negative": bool(
            cint(values.get("allow_negative"))
        ),
    }


def get_overlapping_leave_application(
    employee,
    from_date,
    to_date,
):
    """Return one Open/Approved Leave Application overlapping these dates."""

    rows = frappe.get_all(
        "Leave Application",
        filters=[
            ["Leave Application", "employee", "=", employee],
            ["Leave Application", "docstatus", "<", 2],
            [
                "Leave Application",
                "status",
                "in",
                ["Open", "Approved"],
            ],
            [
                "Leave Application",
                "to_date",
                ">=",
                getdate(from_date),
            ],
            [
                "Leave Application",
                "from_date",
                "<=",
                getdate(to_date),
            ],
        ],
        fields=[
            "name",
            "leave_type",
            "from_date",
            "to_date",
            "status",
        ],
        order_by="from_date asc, creation asc",
        limit_page_length=1,
    )

    if not rows:
        return None

    row = rows[0]

    return {
        "name": row.name,
        "leave_type": row.leave_type,
        "from_date": str(row.from_date),
        "to_date": str(row.to_date),
        "status": row.status,
    }
