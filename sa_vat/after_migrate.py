# -*- coding: utf-8 -*-
# Copyright (c) 2022, Greycube and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_migrate(**args):

    custom_fields = {
        "Sales Invoice": [
            dict(
                fieldtype="Check",
                fieldname="is_bad_debt_cf",
                label="Is Bad Debt",
                insert_after="update_billed_amount_in_sales_order",
                allow_on_submit=1,
                print_hide=1,
            ),
            dict(
                fieldtype="Check",
                fieldname="is_overseas_cf",
                label="Is Overseas",
                insert_after="is_bad_debt_cf",
                print_hide=1,
            ),
        ],
        "Purchase Invoice": [
            dict(
                fieldtype="Check",
                fieldname="is_overseas_cf",
                label="Is Overseas",
                insert_after="apply_tds",
                print_hide=1,
            ),
        ],
    }
    create_custom_fields(custom_fields)
    frappe.db.commit()  # to avoid implicit-commit errors
