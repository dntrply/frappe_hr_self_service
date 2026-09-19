# Frappe HR Self Service

Lightweight employee and approver self-service for Frappe HR leave workflows.

## Status

Early development.

The project is being extracted from a working leave self-service implementation
into a reusable Frappe app. Organization-specific leave policies are deliberately
kept outside this app.

## Goals

Provide a small, secure self-service layer for Frappe HR that allows employees to:

- view their own leave balances;
- see leave types available for selected dates;
- submit leave requests;
- view their own leave requests.

Provide approvers with a simplified workflow to:

- view pending leave requests assigned to them;
- review an individual request;
- approve or reject the request.

## Design principles

- Frappe HR remains authoritative for native leave validation.
- Employee identity is derived server-side from the logged-in user.
- Approver identity is derived server-side from the Leave Application.
- Browser preflight checks are repeated on submission.
- Organization-specific leave policy does not belong in the reusable core.
- Direct dependencies on HRMS implementation details are isolated behind a compatibility layer.

## Requirements

Initial supported target:

- Frappe 16
- Frappe HR / HRMS
- Python 3.14+

## License

MIT
