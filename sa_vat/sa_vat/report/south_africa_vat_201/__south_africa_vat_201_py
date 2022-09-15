# Copyright (c) 2022, Greycube and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.regional.report.vat_audit_report.vat_audit_report import (
    execute as _execute,
)

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
    if filters.get("vat_audit_report"):
        return _execute(filters)

    return get_columns(), get_data(filters)


def get_data(filters):
    data = frappe.db.sql(
        """
with fn as
(
    select 
        'Sales Invoice' voucher_type ,tsi.name voucher_no , tsi.posting_date , 
        'Customer' party_type , tsi.customer party , tsi.taxes_and_charges ,
        tsi.grand_total , tsi.net_total , tsi.total_taxes_and_charges , 
        ti.is_fixed_asset , tstact.is_overseas_cf is_overseas ,
        tstc.rate = 0 is_zero_rated , tsi.write_off_amount ,tsi.debit_to account ,
        tsi.remarks , tsi.is_bad_debt_cf is_bad_debt_cf  
    from `tabSales Invoice` tsi 
    inner join `tabSales Invoice Item` tsii on tsii.parent = tsi.name
    inner join tabItem ti on ti.name = tsii.item_code
    inner join `tabSales Taxes and Charges Template` tstact on tstact.name = tsi.taxes_and_charges 
    inner join (
        select parent , sum(rate) rate 
        from `tabSales Taxes and Charges` tstac 
        group by parent
    ) tstc on tstc.parent  = tstact.name  
    {conditions}
    union all
    select 
        'Purchase Invoice' voucher_type ,tsi.name voucher_no , tsi.posting_date , 
        'Customer' party_type , tsi.supplier party , tsi.taxes_and_charges ,
        tsi.grand_total , tsi.net_total , tsi.total_taxes_and_charges , 
        ti.is_fixed_asset , tstact.is_overseas_cf is_overseas ,
        tstc.rate = 0 is_zero_rated , tsi.write_off_amount ,tsi.credit_to account ,
        tsi.remarks , 0 is_bad_debt_cf 
    from `tabPurchase Invoice` tsi 
    inner join `tabPurchase Invoice Item` tsii on tsii.parent = tsi.name
    inner join tabItem ti on ti.name = tsii.item_code
    inner join `tabPurchase Taxes and Charges Template` tstact on tstact.name = tsi.taxes_and_charges 
    inner join (
        select parent , sum(rate) rate 
        from `tabPurchase Taxes and Charges` tstac 
        group by parent
    ) tstc on tstc.parent  = tstact.name      
    {conditions}
)
    select case
	    when fn.is_bad_debt_cf 
	    	then 'BAD DEBTS SALES TOTAL (17)'
        when fn.voucher_type = 'Sales Invoice'
        and not fn.is_fixed_asset and not fn.is_overseas and not fn.is_zero_rated
                then 'SALES RATE TOTAL (1)'
        when fn.voucher_type = 'Sales Invoice'
        and fn.is_fixed_asset and not fn.is_overseas and not fn.is_zero_rated
                then 'CAPITAL GOODS SOLD TOTAL (1A)'
        when fn.voucher_type = 'Sales Invoice'
        and not fn.is_fixed_asset and not fn.is_overseas and fn.is_zero_rated
                then 'ZERO RATED EXCLUDING GOODS EXPORTED TOTAL (2)'
        when fn.voucher_type = 'Sales Invoice'
        and fn.is_overseas and fn.is_zero_rated
                then 'ZERO RATED ONLY EXPORT GOODS TOTAL (2A)'
        when fn.voucher_type = 'Purchase Invoice'
        and fn.is_fixed_asset and not fn.is_overseas and not fn.is_zero_rated
                then 'CAPITAL GOODS AND SERVICES PURCHASED TOTAL (14)'
        when fn.voucher_type = 'Purchase Invoice'
        and fn.is_fixed_asset and fn.is_overseas and not fn.is_zero_rated
                then 'CAPITAL GOODS IMPORTED TOTAL (14A)'
        when fn.voucher_type = 'Purchase Invoice'
        and not fn.is_fixed_asset and not fn.is_overseas and not fn.is_zero_rated
                then 'OTHER GOODS OR SERVICES PURCHASED TOTAL (15)'
        when fn.voucher_type = 'Purchase Invoice'
        and not fn.is_fixed_asset and fn.is_overseas and not fn.is_zero_rated
                then 'OTHER GOODS IMPORTED NOT CAPITAL GOODS TOTAL (15A)'                
        else 'Unknown' end band , fn.*
    from fn
    order by band , posting_date , voucher_no        
    """.format(
            conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
    )

    if not data:
        return []

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
                    "net_total": sum([x.net_total for x in items]),
                    "grand_total": sum([x.grand_total for x in items]),
                    "total_taxes_and_charges": sum(
                        [x.total_taxes_and_charges for x in items]
                    ),
                },
                {},
            ]
        )

    return out


def get_columns():
    return csv_to_columns(
        """
        Posting Date,posting_date,,,400
        Account,account,Link,Account,180
        Voucher Type,voucher_type,,,150
        Reference,voucher_no,Dynamic Link,voucher_type,200
        Party Type,party_type,,,140
        Party,party,Dynamic Link,party_type,200
        Details,remarks,,,180
        Net Amount,net_total,Currency,,140
        Tax Amount,total_taxes_and_charges,Currency,140
        Gross Amount,grand_total,Currency,140
        is_fixed_asset,is_fixed_asset,,,100
        is_zero_rated,is_zero_rated,,,100
        is_overseas,is_overseas,,,100
        Band,band,,,150        
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
