# Frappe HR Self Service

Lightweight employee and approver self-service for Frappe HR leave workflows.

## Status

Early development.

The project is being extracted from a working leave self-service implementation
into a reusable Frappe app. Organization-specific leave policies are deliberately
kept outside this app.

## Documentation

- [Employee Self-Service UI Starter Guide](docs/EMPLOYEE_SELF_SERVICE_UI_STARTER_GUIDE.md) — worked example using Frappe Workspaces, Custom HTML Blocks, Web Pages, and the public self-service APIs.
- [Leave Self-Service Administration Guide](docs/LEAVE_SELF_SERVICE_ADMIN_GUIDE.md) — generic setup and administration guidance for leave periods, policies, allocations, and cutover.
- [Half-Day Leave](docs/HALF_DAY_LEAVE.md) — native half-day inputs, normalization, HRMS calculation and overlap authority, API fields, and UI guidance.
- [Leave Rejection Reason](docs/LEAVE_REJECTION_REASON.md) — mandatory rejection-reason behavior, API contract, employee visibility, website UI guidance, and deployment checks.

## Goals

Provide a small, secure self-service layer for Frappe HR that allows employees to:

- view their own leave balances;
- see leave types available for selected dates;
- submit full-day and half-day leave requests;
- view their own leave requests, including half-day details and an approver's rejection reason when applicable.

Provide approvers with a simplified workflow to:

- view pending leave requests assigned to them;
- review an individual request, including half-day details;
- approve a request;
- reject a request with a required, auditable reason.

## Design principles

- Frappe HR remains authoritative for native leave validation.
- Employee identity is derived server-side from the logged-in user.
- Approver identity is derived server-side from the Leave Application.
- Browser preflight checks are repeated on submission.
- Native half-day calculation and overlap validation remain authoritative in Frappe HR.
- Rejection reasons are validated and persisted server-side rather than relying on transient browser state.
- Organization-specific leave policy does not belong in the reusable core.
- Direct dependencies on HRMS implementation details are isolated behind a compatibility layer.

## Requirements

Initial supported target:

- Frappe 16
- Frappe HR / HRMS
- Python 3.14+

## License

MIT
