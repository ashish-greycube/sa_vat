# Copyright (c) 2022, Greycube and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.regional.report.vat_audit_report.vat_audit_report import (
    execute as _execute,
)


def execute(filters=None):
    columns, data = _execute(filters)

    if not data:
        return columns, data

    capital_goods_vouchers = get_capital_goods_vouchers(data)

    result = []
    header, capital_data = None, []

    for d in data:
        posting_date = d.get("posting_date", "")

        if not posting_date:
            result.append(d)
            continue

        if "<strong>" in posting_date and not "Total" in posting_date:
            header = posting_date
            if capital_data:
                capital_data.insert(
                    0, {"posting_date": frappe.bold(_("Capital Goods ")) + posting_date}
                )
                total_row = {
                    "posting_date": "<strong>Total</strong>",
                }
                result.extend(capital_data + [total_row] + [{}])
                capital_data = []
            result.append(d)
        elif d.get("voucher_no") in capital_goods_vouchers:
            capital_data.append(d)
        else:
            result.append(d)

    # recalculate totals
    tax_amount, gross_amount, net_amount = 0, 0, 0
    for d in result:
        if not d.get("posting_date"):
            continue

        if d.get("posting_date") == "<strong>Total</strong>":
            d.update(
                {
                    "tax_amount": tax_amount,
                    "gross_amount": gross_amount,
                    "net_amount": net_amount,
                }
            )
            tax_amount, gross_amount, net_amount = 0, 0, 0
        else:
            tax_amount += d.get("tax_amount", 0)
            gross_amount += d.get("gross_amount", 0)
            net_amount += d.get("net_amount", 0)

    return COLUMNS, result


def get_capital_goods_vouchers(data):
    vouchers = [d.get("voucher_no") for d in data if d.get("voucher_no")]

    cond = "where t.parent in (%s)" % (", ".join(["%s"] * len(vouchers)))

    capital_goods_vouchers = frappe.db.sql(
        """
        select t.parent 
        from
        (
            select tpii.parent 
            from `tabPurchase Invoice Item` tpii 
            inner join tabItem ti on ti.item_code = tpii.item_code and ti.is_fixed_asset = 1
            union all
            select tsii.parent 
            from `tabSales Invoice Item` tsii 
            inner join tabItem ti on ti.item_code = tsii.item_code and ti.is_fixed_asset = 1
        ) t	
    {cond}""".format(
            cond=cond
        ),
        tuple(vouchers),
        # debug=True,
    )
    return [d[0] for d in capital_goods_vouchers]


COLUMNS = [
    {
        "fieldname": "posting_date",
        "label": "Posting Date",
        "fieldtype": "Data",
        "width": 300,
    },
    {
        "fieldname": "account",
        "label": "Account",
        "fieldtype": "Link",
        "options": "Account",
        "width": 150,
    },
    {
        "fieldname": "voucher_type",
        "label": "Voucher Type",
        "fieldtype": "Data",
        "width": 140,
        "hidden": 1,
    },
    {
        "fieldname": "voucher_no",
        "label": "Reference",
        "fieldtype": "Dynamic Link",
        "options": "voucher_type",
        "width": 300,
    },
    {
        "fieldname": "party_type",
        "label": "Party Type",
        "fieldtype": "Data",
        "width": 140,
        "hidden": 1,
    },
    {
        "fieldname": "party",
        "label": "Party",
        "fieldtype": "Dynamic Link",
        "options": "party_type",
        "width": 150,
    },
    {"fieldname": "remarks", "label": "Details", "fieldtype": "Data", "width": 250},
    {
        "fieldname": "net_amount",
        "label": "Net Amount",
        "fieldtype": "Currency",
        "width": 130,
    },
    {
        "fieldname": "tax_amount",
        "label": "Tax Amount",
        "fieldtype": "Currency",
        "width": 130,
    },
    {
        "fieldname": "gross_amount",
        "label": "Gross Amount",
        "fieldtype": "Currency",
        "width": 130,
    },
]
