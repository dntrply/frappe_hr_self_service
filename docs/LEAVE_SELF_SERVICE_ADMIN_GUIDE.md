# Leave Self-Service Administration Guide

This guide explains the Frappe HR administration prerequisites that must be in place for `frappe_hr_self_service` to work reliably.

It is intentionally generic. Organization-specific leave policy belongs in your own custom app or operational documentation.

Examples of policy that are **not** defined here include:

- leave entitlement quantities;
- waiting periods;
- leave-type sequencing or priority rules;
- carry-forward rules;
- encashment rules;
- organization-specific cutover decisions;
- branding, Workspace names, and employee-facing labels.

For a worked example of building the employee-facing UI with a Frappe Workspace, Custom HTML Blocks, Web Pages, and these APIs, see:

[Employee Self-Service UI Starter Guide](EMPLOYEE_SELF_SERVICE_UI_STARTER_GUIDE.md)

---

## 1. Purpose

`frappe_hr_self_service` provides a simplified employee and approver layer on top of Frappe HR leave workflows.

The public app does not replace Frappe HR's core documents or validation. Frappe HR remains the system of record for:

- Employees;
- Users;
- Leave Approvers;
- Holiday Lists;
- Leave Policies;
- Leave Policy Assignments;
- Leave Allocations;
- Leave Applications;
- leave balances and ledger behavior;
- native submission and validation rules.

The purpose of this guide is to describe the administrative setup that must exist underneath the self-service experience.

A working self-service installation should allow an employee to:

- log in as their own Frappe user;
- see their leave balances;
- select dates and retrieve eligible leave types;
- submit a leave request;
- view their own leave requests;
- have the configured approver review and approve or reject the request;
- see the resulting leave balance reflect approved leave.

---

## 2. Important principle: saved is not the same as submitted

Many Frappe HR documents are not operational merely because they have been saved.

Where this guide says **Submit**, verify that the document actually shows a submitted state rather than Draft.

A common setup failure is:

```text
Document exists
    but
Document is still Draft
    therefore
Expected leave behavior does not occur
```

For leave setup, always verify document status after configuration.

---

## 3. Core documents and what "ready" means

A typical employee self-service setup depends on the following:

| Document / Setting | Ready state |
|---|---|
| Employee | Active, correct Company, correct Date of Joining |
| User | Enabled and linked to exactly one active Employee |
| Employee role/access | Appropriate employee access is present |
| Employee self-service home | User can reach the organization's employee self-service UI |
| Leave Approver | Set on the Employee |
| Holiday List Assignment | Correct dates and Submitted |
| Leave Policy | Correct policy rows and Submitted, when using the policy-assignment path |
| Leave Policy Assignment | Submitted, when generating entitlement through policy |
| Leave Allocation | Submitted and valid for the relevant date range |
| Leave Application | Created and processed through the normal Frappe HR workflow |

The exact UI names and routes are organization-specific.

---

# Part I - Employee identity and access

## 4. Create or verify the Employee

Open the Employee record and confirm at least:

- Employee Name;
- Company;
- Status = Active;
- Date of Joining = the employee's actual date of joining;
- any other mandatory HR fields required by your installation.

### Verify

The Employee must show the correct Company and actual Date of Joining.

Do not replace the historical Date of Joining with an ERP rollout or migration date.

---

## 5. Create or verify the User

Create a Frappe User for the employee if one does not already exist.

Recommended minimum:

- User is enabled;
- the User has the employee access required by your installation;
- the User is not given HR Manager, System Manager, or other elevated roles unless those roles are genuinely required.

Then link the Employee to the User using the Employee's **User ID** field.

### Verify

Confirm:

- Employee.User ID is not blank;
- the User is enabled;
- exactly one active Employee is linked to that User.

The self-service APIs derive employee identity from the authenticated Frappe user. A clean one-user-to-one-active-employee relationship is therefore important.

---

## 6. Configure the employee self-service home

Your organization may use a Workspace such as `My HR`, `Employee Self Service`, or another name.

Set the user's default Workspace if you want the employee to land there after login.

### Verify

Test with the employee's own account, preferably in a fresh or incognito browser session.

The employee should be able to reach the self-service home without relying on Administrator or System Manager privileges.

For a generic UI pattern, see the [Employee Self-Service UI Starter Guide](EMPLOYEE_SELF_SERVICE_UI_STARTER_GUIDE.md).

---

# Part II - Approver setup

## 7. Set the Leave Approver

On the Employee record, set the appropriate Leave Approver according to your Frappe HR configuration.

The approver should be a valid, enabled Frappe User.

### Verify

Confirm:

- the Employee references the correct approver;
- the approver User exists and is enabled;
- the approver has the permissions or role required by your installation to process leave requests.

The self-service approver workflow still relies on Frappe HR's Leave Application and approval authority.

---

# Part III - Holiday setup

## 8. Configure the Holiday List Assignment

Create the Holiday List Assignment required for the employee and the dates your organization manages in Frappe HR.

A typical assignment includes:

- Applicable For = Employee;
- Employee = the employee being configured;
- Holiday List = the applicable calendar;
- Starts On = the appropriate effective date.

Save and **Submit** the assignment.

### Why this matters

Frappe HR needs the applicable holiday calendar when calculating leave days between the requested From Date and To Date.

It is possible for leave balances to display correctly while date-based eligibility fails because no applicable Holiday List can be found.

### Verify

Confirm:

- the assignment is Submitted;
- the requested leave dates fall within a period for which Frappe HR can resolve a Holiday List.

---

# Part IV - Leave entitlement and allocation

There are two common administrative patterns.

Use the one that matches how your organization is establishing the employee's entitlement.

---

## 9. Pattern A - Generate entitlement from a Leave Policy Assignment

This is the normal pattern when Frappe HR is responsible for creating the employee's entitlement for the applicable leave period.

The flow is:

```text
Employee
  ↓
User + Employee linkage
  ↓
Leave Approver
  ↓
Holiday List Assignment
  ↓
Submitted Leave Policy
  ↓
Submitted Leave Policy Assignment
  ↓
Submitted Leave Allocations generated by Frappe HR
  ↓
Self-service verification
```

---

## 10. Confirm the Leave Policy exists and is submitted

The applicable Leave Policy must already exist and be **Submitted**.

### Verify

Confirm:

- the correct Leave Policy is selected;
- the policy belongs to the intended organizational setup;
- the policy is Submitted.

Submitting the Leave Policy itself does not create an employee's Leave Allocations.

---

## 11. Create the Leave Policy Assignment

Create a Leave Policy Assignment for the employee.

Typical fields include:

- Employee;
- Leave Policy;
- Assignment Based On;
- Leave Period, when applicable;
- effective dates;
- any policy-specific carry-forward option your organization intentionally uses.

Save the document, review it, and then **Submit** it.

### Critical check

A Leave Policy Assignment left in Draft may not generate usable employee Leave Allocations.

### Verify

Confirm:

- status = Submitted;
- employee is correct;
- leave policy is correct;
- leave period or effective dates are correct.

---

## 12. Verify generated Leave Allocations

After the Leave Policy Assignment is submitted, verify the allocations Frappe HR generated.

For each expected Leave Type, check:

- correct Employee;
- correct Leave Type;
- expected allocation quantity according to your policy;
- correct date range;
- Leave Policy Assignment reference is populated when generated from the policy assignment;
- status = Submitted.

`frappe_hr_self_service` reads the resulting Frappe HR leave state; it does not replace the entitlement-generation process.

---

## 13. Pattern B - Import existing opening balances

During an ERP or leave-system cutover, an organization may already know each employee's actual remaining leave balance.

A validated migration pattern is to import those remaining balances as standalone Leave Allocations instead of generating a fresh full-year entitlement for the same period.

The key principle is:

> Avoid unintentionally combining imported opening balances with newly generated entitlement for the same employee and period.

If your organization intentionally uses both, document and review that decision carefully.

---

## 14. Choose a cutover date

Define the date from which Frappe HR becomes authoritative for new leave transactions.

For example:

```text
ERP leave cutover date:       YYYY-MM-DD
Legacy balance date:          close of business on the prior day
```

The exact date and transition policy belong to the implementing organization.

---

## 15. Prepare verified opening balances

HR should provide an auditable opening-balance source.

Useful fields include:

| Column | Meaning |
|---|---|
| Employee ID | Frappe HR Employee ID |
| Employee Name | Human verification |
| Date of Joining | Actual historical Date of Joining |
| Company | Frappe Company |
| Balance As Of | Date to which the balance was reconciled |
| Leave Type balances | Remaining balance for each relevant Leave Type |
| Verified By | HR reviewer |
| Verification Date | Review date |
| Notes | Exceptions or reconciliation notes |

How future-dated approved or pending leave is handled is an organization-specific cutover decision and should be documented before import.

---

## 16. Prepare standalone Leave Allocation imports

Use Frappe's Data Import process for **Leave Allocation** when importing opening balances.

Typical fields may include:

| Column | Typical value |
|---|---|
| Employee | Frappe HR Employee ID |
| Company | Frappe Company |
| Leave Type | Exact configured Leave Type |
| From Date | Cutover/effective date |
| To Date | End of the applicable allocation period |
| Total Leaves Allocated | Verified opening balance |
| New Leaves Allocated | Verified opening balance |
| Description | Opening-balance / cutover note |

When importing standalone opening balances, Leave Policy, Leave Period, and Leave Policy Assignment are normally left unpopulated unless your migration design explicitly requires otherwise.

---

## 17. Import as Draft first

A safer migration sequence is:

- Import Type = Insert New Records;
- keep the uploaded file private;
- leave **Submit After Import** unchecked;
- suppress unnecessary emails if appropriate for your environment;
- review the preview;
- run the import;
- inspect the resulting Draft Leave Allocations.

### Verify drafts

For every imported allocation, verify:

- correct Employee;
- correct Leave Type;
- correct From Date;
- correct To Date;
- correct New Leaves Allocated;
- correct Total Leaves Allocated;
- Leave Policy Assignment is blank for a standalone opening-balance import;
- status = Draft.

Do not submit until the values have been checked.

---

## 18. Submit imported Leave Allocations

After validation, submit the imported Leave Allocations.

### Verify

Each intended allocation should show:

- status = Submitted;
- correct balance;
- correct validity dates;
- expected Leave Policy Assignment linkage, or no linkage for a standalone opening balance.

Then verify the employee's actual balance through Frappe HR and through the self-service UI.

---

# Part V - End-to-end self-service verification

## 19. Verify employee leave balance

Log in as the employee.

Confirm that the self-service UI can load the employee's submitted Leave Allocations through:

```text
frappe_hr_self_service.employee_self_service.get_my_leave_balance
```

If no balance appears, use the troubleshooting section below.

---

## 20. Verify leave eligibility

Select a valid date range in the employee UI.

Confirm that the self-service layer can call:

```text
frappe_hr_self_service.employee_self_service.get_available_leave_types
```

and return the Leave Types permitted by the underlying Frappe HR state and any installed extension rules.

Organization-specific rules such as waiting periods, sequencing, or custom eligibility constraints belong outside the generic public app unless they are implemented through its documented extension points.

---

## 21. Verify leave request submission

Submit a test leave request through:

```text
frappe_hr_self_service.employee_self_service.create_leave_request
```

Confirm that:

- the Leave Application is created for the authenticated employee;
- the dates are correct;
- the Leave Type is correct;
- the expected approver is associated with the request;
- native Frappe HR validation is still enforced.

The browser should not be trusted to supply the employee identity.

---

## 22. Verify My Leave Requests

Confirm that the employee can retrieve their own requests using:

```text
frappe_hr_self_service.employee_self_service.get_my_leave_requests
```

The result should contain only Leave Applications belonging to the Employee derived from the current authenticated user.

---

## 23. Verify approver workflow

Complete one test request when practical:

1. employee submits the request;
2. approver sees the pending request;
3. approver reviews it;
4. approver approves or rejects it;
5. the resulting Leave Application state matches Frappe HR behavior;
6. after approval, the employee's leave balance reflects the approved leave.

This is the strongest proof that the employee, allocation, holiday, approval, and self-service configuration are working together.

---

# Part VI - Readiness checklist

## 24. Employee identity

- [ ] Employee exists
- [ ] Employee is Active
- [ ] Company is correct
- [ ] Date of Joining is correct
- [ ] User is linked
- [ ] exactly one active Employee is linked to the User
- [ ] User is enabled
- [ ] employee has the intended self-service access
- [ ] employee can reach the self-service home

## 25. Approval setup

- [ ] Leave Approver is set
- [ ] Leave Approver User exists and is enabled
- [ ] approver has the required approval permissions/role

## 26. Holiday setup

- [ ] Holiday List Assignment exists
- [ ] correct Holiday List is selected
- [ ] effective date is correct
- [ ] Holiday List Assignment is Submitted

## 27. Policy-generated entitlement path

When using Leave Policy Assignment:

- [ ] Leave Policy is Submitted
- [ ] Leave Policy Assignment exists
- [ ] correct Leave Period/effective dates are selected
- [ ] correct policy is selected
- [ ] Leave Policy Assignment is Submitted
- [ ] expected Leave Allocations were generated
- [ ] generated Leave Allocations are Submitted

## 28. Opening-balance import path

When importing existing balances:

- [ ] cutover/effective date is defined
- [ ] opening balances are verified by HR
- [ ] migration treatment of future approved/pending leave is documented
- [ ] standalone Leave Allocations were imported
- [ ] imported values were reviewed before submission
- [ ] imported allocations are Submitted
- [ ] no unintended duplicate entitlement exists for the same period

## 29. End-to-end test

- [ ] self-service home opens
- [ ] balances are visible
- [ ] date selection successfully checks eligibility
- [ ] expected Leave Types are selectable
- [ ] employee can submit a request
- [ ] employee can view their own requests
- [ ] approver can see the request
- [ ] approver can approve/reject
- [ ] balance changes correctly after approval

---

# Part VII - Troubleshooting

## 30. No leave balance is available

Check in this order:

1. Is the User linked to the correct Employee?
2. Is exactly one active Employee linked to that User?
3. Does the Employee have submitted Leave Allocations?
4. If using the policy-assignment path, is the Leave Policy Assignment Submitted rather than Draft?
5. Did submitting the Leave Policy Assignment generate the expected Leave Allocations?
6. Are those Leave Allocations Submitted?
7. Do their dates include the date being checked?

A saved but Draft Leave Policy Assignment is a common reason expected allocations do not appear.

---

## 31. Balances display but leave eligibility fails

The balance endpoint may work even when Frappe HR cannot calculate leave days for a requested date range.

Check the Employee's Holiday List Assignment.

A typical failure is that no Holiday List can be resolved for the Employee and requested date.

Fix by verifying:

- the correct Holiday List Assignment exists;
- the date range covers the requested date;
- the assignment is Submitted.

---

## 32. Employee does not land on the self-service Workspace

Check the User's default Workspace or equivalent navigation configuration.

After saving, test using a new login or incognito session.

The exact Workspace name is organization-specific.

---

## 33. Employee request exists but balance did not reduce

Check:

- Leave Application status;
- whether the approver actually approved the request;
- whether the document reached the submitted/approved state expected by Frappe HR;
- allocation validity dates;
- any organization-specific leave policy rules.

An Open or Draft request is not equivalent to an approved/submitted leave transaction.

---

## 34. Imported employee has too much leave

Check whether both of these exist for the same period:

- imported opening Leave Allocations; and
- entitlement generated from a Leave Policy Assignment.

This can unintentionally duplicate entitlement.

Stop and review the migration design before processing further leave transactions.

---

## 35. Employee can see another employee's data

The browser should not send an Employee ID and have the server trust that value as the authority for self-service access.

The public self-service endpoints derive the Employee from the logged-in Frappe user.

If you create additional endpoints, follow the same pattern.

---

# Part VIII - Administrative principles

## 36. Verify outcomes, not just configuration screens

Do not consider an employee fully configured merely because all setup forms contain values.

The final proof is:

1. correct balances in the employee self-service UI;
2. correct eligibility for selected dates;
3. successful employee request submission;
4. successful approver action;
5. correct post-approval balance;
6. employee can retrieve their own request history.

---

## 37. Keep policy separate from the reusable self-service layer

`frappe_hr_self_service` should remain reusable.

Examples of organization-specific behavior that should normally remain in a downstream app or operational configuration include:

- leave sequencing;
- waiting periods;
- entitlement formulas;
- proration rules;
- carry-forward policy;
- encashment policy;
- custom notifications;
- employee Workspace branding and routes;
- migration/cutover business decisions.

Use the public app for generic authenticated self-service behavior and documented extension points.

---

## 38. Keep UI configuration reproducible

If your self-service Workspace, Web Pages, Custom HTML Blocks, Custom Fields, or Email Templates are created only in the live database, they may not be reproducible on another site or after a rebuild.

Export organization-specific UI configuration as filtered fixtures from your own custom app.

See the [Employee Self-Service UI Starter Guide](EMPLOYEE_SELF_SERVICE_UI_STARTER_GUIDE.md) for a fixture example.

---

# Part IX - Useful first automation

## 39. Leave setup readiness checker

Before automating document creation, a useful first automation is a read-only readiness checker that reports whether the employee is actually ready for self-service.

For example:

```text
✓ Active Employee
✓ Company configured
✓ User linked
✓ Exactly one active Employee linked to User
✓ Self-service access present
✓ Leave Approver configured
✓ Holiday List Assignment submitted
✓ Leave entitlement source configured
✓ Submitted Leave Allocations found

Overall: READY
```

or identifies exact failures such as:

```text
✗ Leave Policy Assignment is still Draft
✗ No submitted Leave Allocations found
✗ No applicable Holiday List Assignment found
```

A readiness checker is safer as a first automation because it makes configuration observable without making transactional decisions.

---

## 40. Later automation candidates

After the readiness checker is proven, an organization may automate selected administrative steps such as:

- setting the employee's self-service Workspace;
- creating Holiday List Assignments;
- creating Leave Policy Assignments;
- preparing opening-balance import rows;
- verifying generated or imported allocations.

Creation and submission of HR documents should remain explicit and auditable according to the organization's operating controls.

---

# 41. Final readiness summary

A working `frappe_hr_self_service` installation depends on a correctly configured Frappe HR foundation.

The minimum operational chain is:

```text
Active Employee
  ↓
Enabled User linked to that Employee
  ↓
Leave Approver configured
  ↓
Applicable Holiday List
  ↓
Submitted Leave Allocations
  ↓
Employee self-service request
  ↓
Approver action
  ↓
Frappe HR updates the authoritative leave state
```

The public self-service app simplifies how employees and approvers interact with that state; it does not replace the underlying Frappe HR administration required to create it.
