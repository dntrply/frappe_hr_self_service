# Employee Self-Service UI Starter Guide

This guide shows one practical way to build an employee-facing self-service experience on top of `frappe_hr_self_service`.

The goal is not to prescribe a single UI. Instead, it demonstrates a reusable Frappe pattern:

- use a **Workspace** as the employee home page,
- use **Custom HTML Blocks** for compact dashboard content and navigation,
- use dedicated **Web Pages** for employee transactions,
- call the public `frappe_hr_self_service` endpoints from those pages,
- keep organization-specific UI, branding, routes, and fixtures in your own custom app.

The examples below use the neutral name **My HR**. Replace that with whatever fits your organization.

---

## 1. What you are building

A simple employee leave self-service experience can look like this:

```text
My HR workspace
    |
    +-- Request Leave
    |      -> Web Page: /request-leave
    |      -> get_available_leave_types()
    |      -> create_leave_request()
    |
    +-- My Leave Requests
    |      -> Web Page: /my-leave-requests
    |      -> get_my_leave_requests()
    |
    +-- My Leave Balance
           -> Custom HTML Block
           -> get_my_leave_balance()
```

The important design principle is:

> Treat the Workspace as an employee home page or launcher, not as the transaction form itself.

This keeps the employee landing page clean and makes it easy to add other self-service activities later.

---

## 2. Public endpoints used by this guide

The examples use these employee-facing methods from `frappe_hr_self_service.employee_self_service`:

```text
get_my_leave_balance
get_available_leave_types
create_leave_request
get_my_leave_requests
```

Full API method names:

```text
frappe_hr_self_service.employee_self_service.get_my_leave_balance
frappe_hr_self_service.employee_self_service.get_available_leave_types
frappe_hr_self_service.employee_self_service.create_leave_request
frappe_hr_self_service.employee_self_service.get_my_leave_requests
```

### Security model

The browser should **not** send an Employee ID and should not be trusted to decide whose records are returned.

The self-service API resolves the current Employee from the authenticated Frappe user.

Browser code should send business inputs such as:

```text
from_date
to_date
leave_type
reason
```

but not trusted identity fields such as:

```text
employee
employee_user
company_employee_id
```

---

## 3. A 30-minute starter implementation

Start with four pieces:

```text
1. Create a "My HR" Workspace
2. Add a "My HR Actions" Custom HTML Block
3. Create a /request-leave Web Page
4. Create a /my-leave-requests Web Page
```

Once those work, add a leave-balance block and export the configuration as fixtures.

---

# Part I - Build the employee home page

## 4. Create the My HR Workspace

Create a Workspace named:

```text
My HR
```

Keep it sparse. A useful first layout is:

```text
My HR

[ Request Leave ]   [ My Leave Requests ]

My Leave Balance
```

The Workspace is the employee home page. Dedicated pages handle the actual transactions.

---

## 5. Create a My HR Actions Custom HTML Block

Create a Custom HTML Block named:

```text
My HR Actions
```

### HTML

```html
<div class="self-service-actions-grid">

    <a class="self-service-action-card" href="/request-leave">
        <div class="self-service-action-title">Request Leave</div>
        <div class="self-service-action-description">Apply for leave</div>
        <div class="self-service-action-arrow">→</div>
    </a>

    <a class="self-service-action-card" href="/my-leave-requests">
        <div class="self-service-action-title">My Leave Requests</div>
        <div class="self-service-action-description">View your leave requests</div>
        <div class="self-service-action-arrow">→</div>
    </a>

</div>
```

### CSS

```css
.self-service-actions-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(240px, 1fr));
    gap: 16px;
    max-width: 760px;
}

.self-service-action-card {
    position: relative;
    display: block;
    min-height: 96px;
    padding: 18px 46px 18px 20px;
    border: 1px solid var(--border-color);
    border-radius: 10px;
    background: var(--card-bg);
    color: var(--text-color);
    text-decoration: none;
}

.self-service-action-card:hover {
    text-decoration: none;
    background: var(--control-bg);
}

.self-service-action-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 5px;
}

.self-service-action-description {
    font-size: 13px;
    color: var(--text-muted);
}

.self-service-action-arrow {
    position: absolute;
    right: 18px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 20px;
}

@media (max-width: 700px) {
    .self-service-actions-grid {
        grid-template-columns: 1fr;
    }
}
```

Add this block to the **My HR** Workspace.

---

# Part II - Build the Request Leave page

## 6. Create the Request Leave Web Page

Create a Web Page with these settings:

```text
Title: Request Leave
Route: request-leave
Published: Yes
Content Type: HTML
Full Width: Yes
Show Title: No
Show Sidebar: No
Insert Style: Yes
```

The `Content Type: HTML` setting matters. If the page is accidentally created as **Page Builder**, HTML stored in `main_section_html` may not render and the page can appear blank.

---

## 7. Request Leave page HTML

```html
<div class="self-service-page-nav">
    <a href="/desk/my-hr">← My HR</a>
</div>

<div class="self-service-request-leave">
    <div class="self-service-request-heading">
        <h3>Request Leave</h3>
        <div class="self-service-request-caption">
            Choose your dates and available leave type
        </div>
    </div>

    <form class="self-service-leave-form">
        <div class="self-service-field">
            <label>From Date</label>
            <input type="date" class="self-service-from-date">
        </div>

        <div class="self-service-field">
            <label>To Date</label>
            <input type="date" class="self-service-to-date">
        </div>

        <div class="self-service-field">
            <label>Leave Type</label>
            <select class="self-service-leave-type" disabled>
                <option value="">Select dates first</option>
            </select>
        </div>

        <div class="self-service-field">
            <label>Reason</label>
            <textarea class="self-service-reason" rows="3" placeholder="Optional"></textarea>
        </div>

        <div class="self-service-form-message" role="status"></div>

        <button type="submit" class="self-service-submit-button" disabled>
            Request Leave
        </button>
    </form>
</div>
```

Change `/desk/my-hr` if your Workspace route is different.

---

## 8. Request Leave page CSS

```css
.self-service-page-nav {
    max-width: 620px;
    margin: 36px auto 0;
    padding: 0 24px;
    box-sizing: border-box;
}

.self-service-page-nav a {
    color: var(--text-muted);
    text-decoration: none;
    font-size: 14px;
}

.self-service-request-leave {
    max-width: 620px;
    margin: 16px auto 64px;
    padding: 0 24px;
    box-sizing: border-box;
}

.self-service-request-heading {
    margin-bottom: 18px;
}

.self-service-request-caption {
    font-size: 13px;
    color: var(--text-muted);
}

.self-service-leave-form {
    display: grid;
    gap: 16px;
}

.self-service-field {
    display: grid;
    gap: 6px;
}

.self-service-field label {
    font-size: 13px;
    font-weight: 600;
}

.self-service-field input,
.self-service-field select,
.self-service-field textarea {
    width: 100%;
    padding: 8px 10px;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    background: var(--control-bg);
    color: var(--text-color);
    font: inherit;
}

.self-service-form-message {
    min-height: 20px;
    font-size: 13px;
}

.self-service-message-error {
    color: var(--red-600);
}

.self-service-message-success {
    color: var(--green-600);
}

.self-service-message-info {
    color: var(--text-muted);
}

.self-service-submit-button {
    justify-self: start;
    padding: 8px 16px;
    border: 0;
    border-radius: 6px;
    background: var(--primary);
    color: white;
    font-weight: 600;
    cursor: pointer;
}

.self-service-submit-button:disabled {
    opacity: 0.55;
    cursor: not-allowed;
}
```

---

## 9. Request Leave page JavaScript

The page first asks the API which leave types are available for the selected dates, then submits the request.

```javascript
document.addEventListener("DOMContentLoaded", function () {
    const root = document.querySelector(".self-service-request-leave");
    if (!root) return;

    const form = root.querySelector(".self-service-leave-form");
    const fromDate = root.querySelector(".self-service-from-date");
    const toDate = root.querySelector(".self-service-to-date");
    const leaveType = root.querySelector(".self-service-leave-type");
    const reason = root.querySelector(".self-service-reason");
    const message = root.querySelector(".self-service-form-message");
    const submitButton = root.querySelector(".self-service-submit-button");

    function setMessage(text, type = "") {
        message.textContent = text || "";
        message.className = "self-service-form-message";
        if (type) message.classList.add(`self-service-message-${type}`);
    }

    function resetLeaveTypes(text = "Select dates first") {
        leaveType.replaceChildren();
        const option = document.createElement("option");
        option.value = "";
        option.textContent = text;
        leaveType.appendChild(option);
        leaveType.disabled = true;
        submitButton.disabled = true;
    }

    async function loadEligibility() {
        const from = fromDate.value;
        const to = toDate.value;

        resetLeaveTypes();
        setMessage("");

        if (!from || !to) return;

        if (to < from) {
            setMessage("To Date cannot be before From Date.", "error");
            return;
        }

        resetLeaveTypes("Checking available leave...");
        setMessage("Checking available leave...");

        try {
            const params = new URLSearchParams({
                from_date: from,
                to_date: to
            });

            const response = await fetch(
                "/api/method/" +
                "frappe_hr_self_service.employee_self_service." +
                "get_available_leave_types?" +
                params.toString(),
                { credentials: "same-origin" }
            );

            if (!response.ok) {
                throw new Error(`Request failed with status ${response.status}`);
            }

            const data = await response.json();
            const result = data.message || {};

            if (result.existing_request) {
                resetLeaveTypes("Leave already requested");
                setMessage(
                    `You already have a ${result.existing_request.leave_type} request covering these dates.`,
                    "info"
                );
                return;
            }

            const rows = result.leave_types || [];
            const eligible = rows.filter(row => row.eligible);

            leaveType.replaceChildren();

            if (!eligible.length) {
                resetLeaveTypes("No leave available");
                const reasons = [...new Set(rows.map(row => row.reason).filter(Boolean))];
                setMessage(
                    reasons.length ? reasons.join(" ") : "No leave type is available for these dates.",
                    "info"
                );
                return;
            }

            const placeholder = document.createElement("option");
            placeholder.value = "";
            placeholder.textContent = "Select leave type";
            leaveType.appendChild(placeholder);

            for (const row of eligible) {
                const option = document.createElement("option");
                option.value = row.leave_type;
                option.textContent = `${row.leave_type} — ${Number(row.available_for_request)} days available`;
                leaveType.appendChild(option);
            }

            leaveType.disabled = false;

            if (eligible.length === 1) {
                leaveType.value = eligible[0].leave_type;
            }

            submitButton.disabled = !leaveType.value;

            const days = Number(eligible[0].requested_days || 0);
            setMessage(`${days} leave day${days === 1 ? "" : "s"} requested.`, "info");

        } catch (error) {
            console.error(error);
            resetLeaveTypes("Unable to check leave");
            setMessage("Unable to check available leave. Please try again.", "error");
        }
    }

    fromDate.addEventListener("change", () => {
        if (fromDate.value) toDate.min = fromDate.value;
        loadEligibility();
    });

    toDate.addEventListener("change", loadEligibility);
    leaveType.addEventListener("change", () => {
        submitButton.disabled = !leaveType.value;
    });

    form.addEventListener("submit", async event => {
        event.preventDefault();

        if (!fromDate.value || !toDate.value || !leaveType.value) return;

        submitButton.disabled = true;
        submitButton.textContent = "Sending...";
        setMessage("Sending your leave request...");

        try {
            const result = await frappe.xcall(
                "frappe_hr_self_service.employee_self_service.create_leave_request",
                {
                    from_date: fromDate.value,
                    to_date: toDate.value,
                    leave_type: leaveType.value,
                    reason: reason.value.trim()
                }
            );

            setMessage(
                `Leave request ${result.name} has been sent to your leave approver.`,
                "success"
            );
            leaveType.disabled = true;
            submitButton.disabled = true;
            submitButton.textContent = "Request Sent";

        } catch (error) {
            console.error(error);
            submitButton.textContent = "Request Leave";
            submitButton.disabled = !leaveType.value;
            setMessage("The leave request could not be sent. Please try again.", "error");
        }
    });
});
```

The API remains authoritative. Browser-side eligibility is a convenience for the employee, not a replacement for server-side validation.

---

# Part III - Build My Leave Requests

## 10. Create the My Leave Requests Web Page

Create another Web Page:

```text
Title: My Leave Requests
Route: my-leave-requests
Published: Yes
Content Type: HTML
Full Width: Yes
Show Title: No
Show Sidebar: No
Insert Style: Yes
```

### HTML

```html
<div class="self-service-my-leave-requests">
    <div class="self-service-page-nav">
        <a href="/desk/my-hr">← My HR</a>
    </div>

    <h1>My Leave Requests</h1>
    <p class="self-service-intro">
        Your recent leave requests and their current status.
    </p>

    <div id="self-service-leave-request-list">Loading...</div>
</div>
```

### CSS

```css
.self-service-my-leave-requests {
    max-width: 900px;
    margin: 36px auto 64px;
    padding: 0 24px;
    box-sizing: border-box;
}

.self-service-my-leave-requests .self-service-page-nav {
    max-width: none;
    margin: 0 0 18px;
    padding: 0;
}

.self-service-intro {
    color: var(--text-muted);
    margin-bottom: 24px;
}

.self-service-request-table {
    width: 100%;
    border-collapse: collapse;
}

.self-service-request-table th,
.self-service-request-table td {
    padding: 12px 10px;
    border-bottom: 1px solid var(--border-color);
    text-align: left;
}

.self-service-request-table th {
    font-size: 13px;
    color: var(--text-muted);
    font-weight: 600;
}

.self-service-empty {
    padding: 24px 0;
    color: var(--text-muted);
}
```

### JavaScript

```javascript
document.addEventListener("DOMContentLoaded", async function () {
    const root = document.getElementById("self-service-leave-request-list");

    function escapeHtml(value) {
        const div = document.createElement("div");
        div.textContent = value == null ? "" : String(value);
        return div.innerHTML;
    }

    try {
        const response = await fetch(
            "/api/method/frappe_hr_self_service.employee_self_service.get_my_leave_requests",
            { credentials: "same-origin" }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.exception || "Unable to load leave requests.");
        }

        const requests = data.message || [];

        if (!requests.length) {
            root.innerHTML = '<div class="self-service-empty">You have no leave requests.</div>';
            return;
        }

        const rows = requests.map(function (request) {
            return `
                <tr>
                    <td>${escapeHtml(request.name)}</td>
                    <td>${escapeHtml(request.leave_type)}</td>
                    <td>${escapeHtml(request.from_date)}</td>
                    <td>${escapeHtml(request.to_date)}</td>
                    <td>${escapeHtml(request.total_leave_days)}</td>
                    <td>${escapeHtml(request.status)}</td>
                </tr>
            `;
        }).join("");

        root.innerHTML = `
            <table class="self-service-request-table">
                <thead>
                    <tr>
                        <th>Request</th>
                        <th>Leave Type</th>
                        <th>From</th>
                        <th>To</th>
                        <th>Days</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        `;

    } catch (error) {
        root.innerHTML = '<div class="self-service-empty">Unable to load leave requests.</div>';
        console.error(error);
    }
});
```

A dedicated page is often preferable to sending employees to the standard HRMS Leave Application list because it keeps the employee experience focused and avoids exposing broader HR navigation that the employee does not need.

---

# Part IV - Add My Leave Balance

## 11. Create a My Leave Balance Custom HTML Block

Create a Custom HTML Block named:

```text
My Leave Balance
```

The exact rendering depends on the shape returned by the installed version of `get_my_leave_balance`, but the browser call follows this pattern:

```javascript
const response = await fetch(
    "/api/method/frappe_hr_self_service.employee_self_service.get_my_leave_balance",
    { credentials: "same-origin" }
);

const data = await response.json();
const balance = data.message || {};
```

Use that data to render cards, rows, or any other display that fits your employee home page.

---

# Part V - Navigation

## 12. Always provide an obvious path back to the employee home page

Dedicated self-service pages should not become dead ends.

A simple pattern is:

```html
<div class="self-service-page-nav">
    <a href="/desk/my-hr">← My HR</a>
</div>
```

Use the real route for your Workspace.

This is particularly useful when you deliberately avoid sending employees through the standard HRMS module navigation.

---

# Part VI - Persist the UI in your own custom app

## 13. Why fixtures matter

Creating a Workspace, Web Page, or Custom HTML Block in the database is enough to make it work on the current site.

It is **not** enough to make the configuration survive a rebuild, redeployment, new site installation, or migration to another server.

For repeatable deployment, export the configuration as fixtures from your own custom app.

The public `frappe_hr_self_service` app should remain generic.

Your custom app should own:

```text
Workspace
Custom HTML Blocks
Web Pages
Branding
Site-specific routes
Site-specific policy
Site-specific notifications
```

---

## 14. Example fixture configuration

In your custom app's `hooks.py`:

```python
fixtures = [
    {
        "dt": "Workspace",
        "filters": [
            ["name", "=", "My HR"],
        ],
    },
    {
        "dt": "Custom HTML Block",
        "filters": [
            [
                "name",
                "in",
                [
                    "My HR Actions",
                    "My Leave Balance",
                ],
            ],
        ],
    },
    {
        "dt": "Web Page",
        "filters": [
            [
                "name",
                "in",
                [
                    "request-leave",
                    "my-leave-requests",
                ],
            ],
        ],
    },
]
```

Then export:

```bash
bench --site your-site.example.com export-fixtures --app your_custom_app
```

Review the generated files before committing them.

A typical result might include:

```text
your_custom_app/
    fixtures/
        workspace.json
        custom_html_block.json
        web_page.json
```

---

# Part VII - Recommended ownership boundary

## 15. What belongs in frappe_hr_self_service

The reusable public app should own generic behavior such as:

```text
Current employee resolution
Leave balance API
Leave eligibility API
Leave request creation API
Employee leave request list API
Approver APIs
Compatibility helpers
Extension points
```

## 16. What belongs in your custom app

Your organization-specific app should normally own:

```text
Employee Workspace
Custom HTML Blocks
Web Pages
Branding
Labels
Navigation
Site-specific policy
Site-specific notifications
Additional organization-specific validation
```

This separation keeps `frappe_hr_self_service` useful to many organizations without imposing one organization's UX.

---

# Part VIII - Troubleshooting

## 17. Web Page is blank

Check:

```text
Content Type = HTML
```

If the page is set to **Page Builder**, HTML stored in `main_section_html` may not render as expected.

## 18. API method works in code but the browser cannot find it

If you added or changed a Python method in a running environment, the web worker may still have the old module loaded.

Restart the relevant backend/web process, then clear the site cache.

In containerized installations, copying a changed Python file into a running container is only temporary unless the image or persistent source is updated.

## 19. Changes disappear after recreating containers

Make sure:

```text
Python source is committed
UI configuration is exported as fixtures
The deployment image is built from the updated repositories
```

## 20. Workspace link opens the normal HRMS list and employees get lost

For employee self-service, a dedicated Web Page is often clearer than linking directly to a standard DocType list.

For example:

```text
Avoid:
    /app/leave-application

Prefer:
    /my-leave-requests
```

## 21. Employee can see another employee's data

Do not accept an Employee ID from browser input and use it as the authority for a self-service query.

The self-service API should derive the Employee from the logged-in Frappe user.

If you create new endpoints, follow the same pattern.

## 22. Database configuration works but is not reproducible

Export the relevant Workspace, Custom HTML Blocks, Web Pages, Custom Fields, Email Templates, and other configuration as filtered fixtures in your custom app.

Avoid exporting unrelated site configuration.

---

# Part IX - Extending the pattern beyond Leave

## 23. The same approach can be reused

Once you understand these three building blocks:

```text
Workspace
Custom HTML Block
Web Page
```

you can use the same pattern for other employee self-service functions.

Examples might include:

```text
Attendance
Expense claims
Employee profile updates
Payslip access
Shift information
Training requests
Asset requests
HR letters
Internal service requests
```

Each activity can have:

```text
A card on the employee Workspace
A dedicated Web Page
A small public API surface
An explicit route back to the employee home page
```

This keeps the employee experience focused while ERPNext / Frappe HR remains the system of record.

---

# Part X - Suggested project structure

## 24. Public app plus custom app

A practical deployment can look like:

```text
frappe_hr_self_service/
    frappe_hr_self_service/
        employee_context.py
        employee_self_service.py
        leave_approval.py
        hrms_compat.py
        ...

your_custom_app/
    your_custom_app/
        hooks.py
        ...
        fixtures/
            workspace.json
            custom_html_block.json
            web_page.json
```

The public app supplies reusable self-service capabilities.

The custom app supplies the organization's employee experience.

---

# Part XI - Optional examples directory

## 25. Keep examples separate from installed fixtures

Once this guide is stable, the public repository can optionally add:

```text
examples/
    employee_self_service/
        actions.html
        actions.css
        request_leave.html
        request_leave.css
        request_leave.js
        my_leave_requests.html
        my_leave_requests.css
        my_leave_requests.js
```

These should remain examples rather than automatically installed fixtures.

That lets adopters copy, modify, and brand the UI without the public app forcing particular Workspace names, routes, labels, or styling.

---

## 26. Final architecture summary

The recommended pattern is:

```text
frappe_hr_self_service
    |
    +-- reusable authenticated APIs
    +-- generic employee context
    +-- generic HRMS compatibility
    +-- extension points

your_custom_app
    |
    +-- employee Workspace
    +-- Custom HTML Blocks
    +-- Web Pages
    +-- branding and labels
    +-- site-specific policy and notifications
    +-- fixtures
```

The result is a clean separation between reusable self-service capability and organization-specific employee experience.
