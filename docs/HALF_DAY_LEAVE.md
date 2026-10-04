# Half-Day Leave

`frappe_hr_self_service` supports native Frappe HR half-day leave fields without duplicating Frappe HR leave-day arithmetic or overlap rules.

## Design principle

Frappe HR remains authoritative for native leave calculation and validation.

The self-service layer passes the native `half_day` and `half_day_date` values into the HRMS leave calculation and Leave Application. It does not introduce AM/PM semantics or maintain separate half-day arithmetic.

## Employee preflight API

Use:

```text
frappe_hr_self_service.employee_self_service.get_available_leave_types
```

In addition to `from_date` and `to_date`, the method accepts:

```text
half_day
half_day_date
```

`half_day` is normalized to `0` or `1` before it is passed to the HRMS calculation boundary.

### Single-day half-day request

For a single-day request, send:

```text
from_date = 2026-10-15
to_date = 2026-10-15
half_day = 1
```

The self-service API normalizes:

```text
half_day_date = 2026-10-15
```

The response includes:

```text
half_day
half_day_date
```

and each eligible leave type contains the HRMS-calculated `requested_days`. A normal working-day half-day request therefore typically reports `0.5`, subject to native HRMS rules.

### Multi-day request with one half-day

For a multi-day request with one half-day, send the date explicitly:

```text
from_date = 2026-10-15
to_date = 2026-10-17
half_day = 1
half_day_date = 2026-10-17
```

For multi-day half-day requests, `half_day_date` is required and must fall within the requested date range.

The server rejects a missing or out-of-range half-day date before calculating eligibility.

## Creating the Leave Application

Use:

```text
frappe_hr_self_service.employee_self_service.create_leave_request
```

The creation API accepts the same half-day inputs:

```text
half_day
half_day_date
```

Submission repeats the half-day-aware eligibility preflight rather than trusting browser state. The normalized values from that server-side preflight are then written to the native Frappe HR Leave Application fields:

```text
half_day
half_day_date
```

The response also includes those normalized values.

## Native overlap validation

For full-day preflight, the reusable app can detect a simple existing overlapping request before submission.

For half-day requests, overlap validation is deliberately deferred to Frappe HR. Native HRMS has specific half-day overlap behavior, including handling more than one half-day request on the same date. Reimplementing that logic in the self-service layer would risk diverging from Frappe HR.

The browser should therefore treat preflight as a convenience. The Leave Application insert remains authoritative.

## Reading half-day details

Employee request history returned by:

```text
frappe_hr_self_service.employee_self_service.get_my_leave_requests
```

includes:

```text
half_day
half_day_date
```

Approver methods also expose these fields:

```text
frappe_hr_self_service.leave_approval.get_pending_leave_approvals
frappe_hr_self_service.leave_approval.get_leave_for_approval
```

A UI can therefore distinguish:

- a normal full-day request;
- a single-day half-day request;
- a multi-day request where one specific date is the half day.

## UI guidance

A practical employee UI can use a `Half Day` checkbox.

For a single-day request, no separate date selector is needed because the server uses the selected day as `half_day_date`.

For a multi-day request, show a `Half Day Date` control and require the employee to select a date inside the requested range before running eligibility.

Do not calculate `0.5` or subtract half a day in browser code. Display the server-provided `requested_days` value instead.

Likewise, approver and employee-history views should display the half-day information returned by the API rather than infer it from the number of requested days.
