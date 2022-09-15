# Copyright (c) 2022, Greycube and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.regional.report.vat_audit_report.vat_audit_report import (
    execute as _execute,
)
from frappe.utils import cint

BANDS = [
    "SALES RATE TOTAL (1)",
    "CAPITAL GOODS SOLD TOTAL (1A)",
    "ZERO RATED EXCLUDING GOODS EXPORTED TOTAL (2)",
    "ZERO RATED ONLY EXPORT GOODS TOTAL (2A)",
    "CAPITAL GOODS AND SERVICES PURCHASED TOTAL (14)",
    "CAPITAL GOODS IMPORTED TOTAL (14A)",
    "OTHER GOODS OR SERVICES PURCHASED TOTAL (15)",
    "OTHER GOODS IMPORTED NOT CAPITAL GOODS TOTAL (15A)",
    "BAD DEBTS SALES TOTAL (17)",
]


def execute(filters=None):
    columns, data = _execute(filters)

    if filters.get("vat_audit_report") or not data:
        return columns, data

    return get_columns(), get_data(filters, data)


def get_data(filters, data):
    invoice_details = frappe.db.sql(
        """ 
    select 
        tsi.name voucher_no , tsi.is_overseas_cf is_overseas , 
        tsi.is_bad_debt_cf is_bad_debt_cf ,
        max(ti.is_fixed_asset) is_fixed_asset  
    from `tabSales Invoice` tsi 
    inner join `tabSales Invoice Item` tsii on tsii.parent = tsi.name
    inner join tabItem ti on ti.name = tsii.item_code
    {conditions}
    group by tsi.name , tsi.is_overseas_cf , tsi.is_bad_debt_cf 
    union all
    select 
        tsi.name voucher_no , tsi.is_overseas_cf is_overseas , 
        0 is_bad_debt_cf ,
        max(ti.is_fixed_asset) is_fixed_asset  
    from `tabPurchase Invoice` tsi 
    inner join `tabPurchase Invoice Item` tsii on tsii.parent = tsi.name
    inner join tabItem ti on ti.name = tsii.item_code
    {conditions}
    group by tsi.name , tsi.is_overseas_cf      
    """.format(
            conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
    )

    data = [frappe._dict(d) for d in data if d and d.get("voucher_no")]

    for d in data:
        d["is_zero_rated"] = not d.tax_amount
        for detail in filter(lambda x: x.voucher_no == d.voucher_no, invoice_details):
            d.update(detail)
            if d.voucher_type == "Sales Invoice":
                if d.is_bad_debt_cf:
                    d["band"] = "BAD DEBTS SALES TOTAL (17)"
                elif not d.is_fixed_asset and not d.is_overseas and not d.is_zero_rated:
                    d["band"] = "SALES RATE TOTAL (1)"
                elif d.is_fixed_asset and not d.is_overseas and not d.is_zero_rated:
                    d["band"] = "CAPITAL GOODS SOLD TOTAL (1A)"
                elif not d.is_fixed_asset and not d.is_overseas and d.is_zero_rated:
                    d["band"] = "ZERO RATED EXCLUDING GOODS EXPORTED TOTAL (2)"
                elif d.is_overseas and d.is_zero_rated:
                    d["band"] = "ZERO RATED ONLY EXPORT GOODS TOTAL (2A)"
            elif d.voucher_type == "Purchase Invoice":
                if d.is_fixed_asset and not d.is_overseas and not d.is_zero_rated:
                    d["band"] = "CAPITAL GOODS AND SERVICES PURCHASED TOTAL (14)"
                if d.is_fixed_asset and d.is_overseas and not d.is_zero_rated:
                    d["band"] = "CAPITAL GOODS IMPORTED TOTAL (14A)"
                if not d.is_fixed_asset and not d.is_overseas and not d.is_zero_rated:
                    d["band"] = "OTHER GOODS OR SERVICES PURCHASED TOTAL (15)"
                if not d.is_fixed_asset and d.is_overseas and not d.is_zero_rated:
                    d["band"] = "OTHER GOODS IMPORTED NOT CAPITAL GOODS TOTAL (15A)"

    out = []

    for band in BANDS:
        out.extend(
            [
                {
                    "posting_date": band.replace(" TOTAL ", " "),
                }
            ]
        )

        items = list(filter(lambda x: x.band == band, data))
        out.extend(items)
        out.extend(
            [
                {
                    "bold": 1,
                    "posting_date": band,
                    "net_amount": sum([x.net_amount for x in items]),
                    "gross_amount": sum([x.gross_amount for x in items]),
                    "tax_amount": sum([x.tax_amount for x in items]),
                },
                {},
            ]
        )

    out.extend(list(filter(lambda x: not x.band, data)))

    return out


def get_columns():
    return csv_to_columns(
        """
        Posting Date,posting_date,,,300
        Account,account,Link,Account,130
        Voucher Type,voucher_type,,,130
        Reference,voucher_no,Dynamic Link,voucher_type,200
        Party Type,party_type,,,140
        Party,party,Dynamic Link,party_type,130
        Details,remarks,,,180
        Net Amount,net_amount,Currency,,140
        Tax Amount,tax_amount,Currency,140
        Gross Amount,gross_amount,Currency,140
        is_fixed_asset,is_fixed_asset,,,100
        is_zero_rated,is_zero_rated,,,100
        is_overseas,is_overseas,,,100
        """
    )


def csv_to_columns(csv_str):
    props = ["label", "fieldname", "fieldtype", "options", "width"]
    return [
        zip(props, [x.strip() for x in col.split(",")])
        for col in csv_str.split("\n")
        if col.strip()
    ]


def get_conditions(filters):
    conditions = ["tsi.docstatus = 1"]
    if filters.get("from_date"):
        conditions.append("tsi.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("tsi.posting_date <= %(to_date)s")
    if filters.get("company"):
        conditions.append("tsi.company = %(company)s")

    return conditions and " where " + " and ".join(conditions) or ""
