"""Employee-facing leave self-service API."""

import frappe

from frappe_hr_self_service.employee_context import get_current_employee
from frappe_hr_self_service.hrms_compat import get_leave_balance_map


@frappe.whitelist()
def get_my_leave_balance():
    """Return normalized leave balances for the logged-in employee."""

    employee = get_current_employee()

    return get_leave_balance_map(employee.name)
