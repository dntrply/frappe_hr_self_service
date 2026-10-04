# Leave Rejection Reason

`frappe_hr_self_service` supports an auditable rejection reason when an approver rejects a Frappe HR Leave Application.

This is generic self-service behavior. Organization-specific wording, page design, branding, and notification templates should remain in the consuming custom app.

## What the app adds

The app installs one Custom Field on `Leave Application`:

```text
Fieldname: custom_rejection_reason
Label: Rejection Reason
Type: Small Text
Permission Level: 1
```

The field is shown when the Leave Application status is `Rejected` and is conditionally mandatory in that state. It is not marked `allow_on_submit`, so normal submitted-document rules prevent later editing through the document form.

The fixture is owned by `frappe_hr_self_service` and is installed or updated by normal Frappe fixture synchronization, for example during:

```bash
bench --site <site> migrate
```

## Server-side enforcement

A `before_submit` hook validates rejected Leave Applications. If `status == "Rejected"`, `custom_rejection_reason` must contain a non-blank value.

This matters because the requirement is not only a browser rule. A rejected Leave Application submitted through another UI or integration still passes through the server-side validation.

Blank or whitespace-only reasons are rejected with:

```text
Please provide a reason for rejecting this leave request.
```

## Approver API

Use:

```text
frappe_hr_self_service.leave_approval.reject_leave
```

This method accepts:

```text
name    Leave Application name
reason  Rejection reason; required and non-blank
```

Example:

```javascript
const result = await frappe.xcall(
    "frappe_hr_self_service.leave_approval.reject_leave",
    {
        name: leaveName,
        reason: rejectionReason
    }
);
```

The endpoint:

1. verifies that the logged-in user is the Leave Application's designated approver;
2. verifies that the application is still open and unsubmitted;
3. preserves native Frappe HR submit permission checks;
4. trims and validates the rejection reason;
5. stores it in `custom_rejection_reason`;
6. sets `status = "Rejected"` and submits the Leave Application.

A successful response includes:

```text
name
status
docstatus
rejection_reason
message
```

where `message` is `Leave request rejected.`.

## Reading the rejection reason

### Approver review

`frappe_hr_self_service.leave_approval.get_leave_for_approval` returns:

```text
rejection_reason
```

in addition to the normal leave-request details.

### Employee request history

`frappe_hr_self_service.employee_self_service.get_my_leave_requests` also returns:

```text
rejection_reason
```

for each Leave Application belonging to the logged-in employee.

A consuming employee UI can therefore show the reason only when the request is rejected, for example:

```text
Rejected
Rejection reason: Coverage is unavailable.
```

Older rejected Leave Applications can legitimately have an empty rejection reason if they were processed before this feature was installed.

## Recommended website UI pattern

For an employee- or approver-facing Frappe **Web Page**, collect the rejection reason with normal website-compatible HTML or browser controls and then call the public API.

Do not assume Desk-only form controls are available on a website page. In particular, a Web Page may not load the Desk control factory required by `frappe.prompt()`.

A minimal website-safe pattern is:

```javascript
const entered = window.prompt(
    "Please enter the reason for rejecting this leave request:"
);

if (entered === null) return;

const reason = String(entered).trim();

if (!reason) {
    window.alert(
        "Please provide a reason for rejecting this leave request."
    );
    return;
}

const result = await frappe.xcall(
    "frappe_hr_self_service.leave_approval.reject_leave",
    {
        name: leaveName,
        reason
    }
);
```

A richer implementation may use a normal HTML `<dialog>` or an inline form instead.

After a successful rejection, keep a confirmation visible on the final page so the approver can verify both the resulting state and the captured reason, for example:

```text
Status: Rejected

Leave request rejected.
Rejection reason: Coverage is unavailable.
```

## Security and ownership

The browser is not trusted to choose the approver or bypass Frappe HR submission rules. Authorization and validation remain server-side.

The reusable app owns:

- the rejection-reason field;
- the server-side mandatory-reason validation;
- the approver API contract;
- exposure of the reason to the affected employee.

A consuming custom app owns organization-specific UI, wording, routes, page fixtures, and notification policy.

## Deployment checklist

After installing or updating a version that introduces this feature:

```bash
bench --site <site> migrate
bench --site <site> clear-cache
bench --site <site> clear-website-cache
```

If Python source changed in a long-running deployment, reload or restart the relevant Frappe processes according to that deployment's process/container model.

Verify end-to-end that:

- an approver cannot reject without a reason;
- the Leave Application is submitted with `status = "Rejected"`;
- `custom_rejection_reason` contains the submitted reason;
- the employee sees the reason in their leave-request history;
- a website UI does not depend on Desk-only dialog controls.
