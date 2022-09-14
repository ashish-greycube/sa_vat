from . import __version__ as app_version

app_name = "sa_vat"
app_title = "SA VAT"
app_publisher = "Greycube"
app_description = "VAT customizations for South Africa"
app_email = "admin@greycube.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sa_vat/css/sa_vat.css"
# app_include_js = "/assets/sa_vat/js/sa_vat.js"

# include js, css files in header of web template
# web_include_css = "/assets/sa_vat/css/sa_vat.css"
# web_include_js = "/assets/sa_vat/js/sa_vat.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "sa_vat/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "sa_vat.utils.jinja_methods",
# 	"filters": "sa_vat.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "sa_vat.install.before_install"
# after_install = "sa_vat.install.after_install"
after_migrate = "sa_vat.after_migrate.after_migrate"

# Uninstallation
# ------------

# before_uninstall = "sa_vat.uninstall.before_uninstall"
# after_uninstall = "sa_vat.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sa_vat.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"sa_vat.tasks.all"
# 	],
# 	"daily": [
# 		"sa_vat.tasks.daily"
# 	],
# 	"hourly": [
# 		"sa_vat.tasks.hourly"
# 	],
# 	"weekly": [
# 		"sa_vat.tasks.weekly"
# 	],
# 	"monthly": [
# 		"sa_vat.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "sa_vat.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sa_vat.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "sa_vat.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"sa_vat.auth.validate"
# ]
