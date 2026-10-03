app_name = "frappe_hr_self_service"
app_title = "Frappe HR Self Service"
app_publisher = "dntrply"
app_description = "Lightweight employee and approver self-service for Frappe HR leave workflows."
app_email = ""
app_license = "mit"

required_apps = ["hrms"]

fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            [
                "name",
                "=",
                "Leave Application-custom_rejection_reason",
            ]
        ],
    }
]

doc_events = {
    "Leave Application": {
        "before_submit": (
            "frappe_hr_self_service.leave_approval."
            "validate_rejection_reason"
        ),
    }
}
