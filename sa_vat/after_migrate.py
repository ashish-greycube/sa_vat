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
            ),
        ],
        "Purchase Taxes and Charges Template": [
            dict(
                fieldtype="Check",
                fieldname="is_overseas_cf",
                label="Is Overseas",
                insert_after="disabled",
            ),
        ],
        "Sales Taxes and Charges Template": [
            dict(
                fieldtype="Check",
                fieldname="is_overseas_cf",
                label="Is Overseas",
                insert_after="disabled",
            ),
        ],
    }
    create_custom_fields(custom_fields)
    frappe.db.commit()  # to avoid implicit-commit errors
