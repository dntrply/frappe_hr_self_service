# Frappe HR Self Service

Lightweight employee and approver self-service for Frappe HR leave workflows.

## Status

Early development.

The project is being extracted from a working leave self-service implementation
into a reusable Frappe app. Organization-specific leave policies are deliberately
kept outside this app.

## Why this exists

Frappe HR already provides the underlying leave workflow, validation, balances,
approvals, and Leave Application model. This project is not intended to replace
or duplicate that functionality.

The problem it addresses is the employee-facing experience.

In many organizations, an employee who simply wants to request leave, check a
balance, or review the status of a request does not need the full Desk or HR
workspace. A smaller self-service surface can make those common actions easier
to understand while still using Frappe HR as the authoritative system of record.

`frappe_hr_self_service` therefore provides a narrow, reusable API layer for
employee and approver leave actions. Organizations can build their own simple
employee experience on top of those APIs using Frappe Workspaces, Web Pages,
Custom HTML Blocks, or another frontend.

The intended separation is:

```text
Organization-specific employee UI
            |
            v
frappe_hr_self_service
            |
            v
       Frappe HR / HRMS
```

Frappe HR remains responsible for native leave calculation and validation. The
self-service layer handles authenticated employee context, a smaller API surface,
and a few reusable workflow conveniences. Organization-specific policies,
branding, navigation, and business rules should stay in the organization's own
custom app rather than in this reusable core.

## Screenshots

The screenshots below show one example of an organization-specific employee
experience built on top of `frappe_hr_self_service`. The UI itself is not part of
the reusable core; it illustrates how the APIs can be presented to employees and
approvers.

1. **Employee home / self-service workspace** — a simple starting point for common HR actions.
   <img width="1437" height="887" alt="Employee self-service workspace" src="https://github.com/user-attachments/assets/1db4a32b-f8e0-4bbf-bcca-e016affea31a" />

2. **Request Leave** — including full-day and half-day leave selection and eligibility feedback.
   <img width="953" height="847" alt="Request Leave page with half-day selection" src="https://github.com/user-attachments/assets/a6f7162a-4e47-401a-95ab-2fdb147d9226" />

3. **Approver review** — showing the simplified leave-review experience and half-day details.
   <img width="963" height="862" alt="Approver review page with half-day details" src="https://github.com/user-attachments/assets/62082237-7b3a-4353-82e5-28c06d3c24c4" />

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
