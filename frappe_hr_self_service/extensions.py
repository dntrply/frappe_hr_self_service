"""Extension points for organization-specific leave rules."""

import frappe


LEAVE_ELIGIBILITY_HOOK = (
    "frappe_hr_self_service_leave_eligibility"
)


def get_leave_eligibility_extension_reason(
    *,
    employee,
    company,
    leave_type,
    from_date,
    to_date,
    requested_days,
    balance,
    available_for_request,
):
    """Return the first organization extension reason that blocks leave.

    Extension callbacks may veto an otherwise eligible leave type by
    returning a non-empty reason string. Returning None or an empty value
    leaves the core eligibility result unchanged.
    """

    for method in frappe.get_hooks(
        LEAVE_ELIGIBILITY_HOOK
    ):
        reason = frappe.get_attr(method)(
            employee=employee,
            company=company,
            leave_type=leave_type,
            from_date=from_date,
            to_date=to_date,
            requested_days=requested_days,
            balance=balance,
            available_for_request=available_for_request,
        )

        if reason:
            return str(reason)

    return None
