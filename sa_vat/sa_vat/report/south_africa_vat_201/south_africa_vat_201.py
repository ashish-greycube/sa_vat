# Copyright (c) 2022, Greycube and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.regional.report.vat_audit_report.vat_audit_report import (
    execute as _execute,
)


def execute(filters=None):
    columns, data = _execute(filters)
    if filters.get("vat_audit_report") or not data:
        return columns, data

    _data = []

    details = get_details(data)

    section = ""
    for idx, d in enumerate(data):
        # remove blank rows
        if not d:
            continue
        # remove total rows
        if not d.get("account") and d.get("net_amount"):
            continue
        # remove section rows
        label = d.get("posting_date")
        if not d.get("net_amount"):
            if not label == section:
                section = label
            continue

        d.update({"section": section})
        d.update(details.get(d.get("voucher_no"), {}))

        if d.get("is_fixed_asset"):
            d.update({"new_section": "Capital Goods " + d.get("section")})
        elif "Export" in d.get("taxes_and_charges"):
            d.update(
                {
                    "new_section": d.get("taxes_and_charges").replace(" - SAV", "")
                    + " "
                    + d.get("section")
                }
            )
        else:
            d.update({"new_section": d.get("section")})

        _data.append(d)

    original_order = []
    for d in data:
        if not d.get("section") in original_order:
            original_order.append(d.get("section"))

    print(original_order)

    _data = sorted(
        _data,
        key=lambda x: str(original_order.index(x.get("section"))).rjust(4, "0")
        + x.get("section", "")
        + x.get("new_section", ""),
    )

    with_totals = []

    for idx, d in enumerate(_data):
        if not idx:
            with_totals.append({"posting_date": _data[idx].get("new_section")})

        with_totals.append(d)
        if idx == len(_data) - 1:
            with_totals.append(
                {"posting_date": frappe.bold("Total " + d.get("new_section"))}
            )
            with_totals.append({})
        elif not _data[idx + 1].get("new_section") == d.get("new_section"):
            with_totals.append(
                {"posting_date": frappe.bold("Total " + d.get("new_section"))}
            )
            with_totals.append({})
            with_totals.append(
                {"posting_date": frappe.bold(_data[idx + 1].get("new_section"))}
            )

    return COLUMNS, with_totals


def get_details(data):
    vouchers = [d.get("voucher_no") for d in data if d.get("voucher_no")]
    details = frappe.db.sql(
        """
    select *
    from 
    (
        select ci.parent , pi.taxes_and_charges , max(ti.is_fixed_asset) is_fixed_asset
        from `tabPurchase Invoice Item` ci 
        inner join `tabPurchase Invoice` pi on pi.name = ci.parent 
        inner join tabItem ti on ti.item_code = ci.item_code 
        group by ci.parent, pi.taxes_and_charges 
        union all
        select ci.parent , pi.taxes_and_charges , max(ti.is_fixed_asset) is_fixed_asset
        from `tabSales Invoice Item` ci 
        inner join `tabSales Invoice` pi on pi.name = ci.parent 
        inner join tabItem ti on ti.item_code = ci.item_code 
        group by ci.parent, pi.taxes_and_charges 
    ) t {cond}
    """.format(
            cond="where t.parent in (%s)" % (", ".join(["%s"] * len(vouchers)))
        ),
        tuple(vouchers),
        as_dict=True,
    )

    return {d.parent: d for d in details}


def __execute(filters=None):
    columns, data = _execute(filters)

    if not data:
        return columns, data

    # print(data)

    capital_goods_vouchers = get_capital_goods_vouchers(data)

    result = []
    header, capital_data = None, []

    for d in data:
        posting_date = d.get("posting_date", "")
        if posting_date and "%" in posting_date:
            header = posting_date

        if not posting_date:
            result.append(d)
            continue

        if d.get("voucher_no"):
            if not d.get("voucher_no") in capital_goods_vouchers:
                result.append(d)
            else:
                capital_data.append(d)
        elif "Total" in posting_date:
            d.update(
                {"posting_date": posting_date.replace("Total", header + " Total ")}
            )
            result.append(d)
            if capital_data:
                band_title = frappe.bold(_("Capital Goods ")) + header
                result.extend(
                    [
                        {},
                        {"posting_date": frappe.bold(_("Capital Goods ")) + header},
                    ]
                    + capital_data
                    + [{"posting_date": band_title + frappe.bold(_(" Total"))}]
                )
                capital_data = []
        else:
            result.append(d)

        # if "<strong>" in posting_date and not "Total" in posting_date:
        #     header = posting_date
        #     if capital_data:
        #         capital_data.insert(
        #             0, {"posting_date": frappe.bold(_("Capital Goods ")) + posting_date}
        #         )
        #         total_row = {
        #             "posting_date": "<strong>Total</strong>",
        #         }
        #         result.extend(capital_data + [total_row] + [{}])
        #         capital_data = []
        #     result.append(d)
        # elif d.get("voucher_no") in capital_goods_vouchers:
        #     capital_data.append(d)

    # recalculate totals
    tax_amount, gross_amount, net_amount = 0, 0, 0
    for d in result:
        if not d.get("posting_date"):
            continue

        if " Total" in d.get("posting_date", ""):
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

    filtered = frappe.db.sql(
        """
        select t.parent 
        from
        (
            select tpii.parent 
            from `tabPurchase Invoice Item` tpii 
            inner join `tabPurchase Invoice` tpi on tpi.name = tpii.parent 
            and tpi.taxes_and_charges <> '{import_taxes_and_charges}'
            inner join tabItem ti on ti.item_code = tpii.item_code and ti.is_fixed_asset = 1
            
            union all
            select tsii.parent 
            from `tabSales Invoice Item` tsii 
            inner join `tabSales Invoice` tsi on tsi.name = tsii.parent 
            and tsi.taxes_and_charges <> '{export_taxes_and_charges}'
            inner join tabItem ti on ti.item_code = tsii.item_code and ti.is_fixed_asset = 1
        ) t	
    {cond}""".format(
            cond=cond,
            import_taxes_and_charges="Import Zero Rated",
            export_taxes_and_charges="Export Zero Rated",
        ),
        tuple(vouchers),
    )
    return [d[0] for d in filtered]


def get_zero_rated_vouchers(data):
    vouchers = [d.get("voucher_no") for d in data if d.get("voucher_no")]

    cond = "where t.parent in (%s)" % (", ".join(["%s"] * len(vouchers)))

    filtered = frappe.db.sql(
        """
        select t.parent 
        from
        (
            select tpii.parent 
            from `tabPurchase Invoice Item` tpii 
            inner join `tabPurchase Invoice` tpi on tpi.name = tpii.parent 
            and tpi.taxes_and_charges = '{import_taxes_and_charges}'
            inner join tabItem ti on ti.item_code = tpii.item_code and ti.is_fixed_asset = 1
            
            union all
            select tsii.parent 
            from `tabSales Invoice Item` tsii 
            inner join `tabSales Invoice` tsi on tsi.name = tsii.parent 
            and tsi.taxes_and_charges = '{export_taxes_and_charges}'
            inner join tabItem ti on ti.item_code = tsii.item_code and ti.is_fixed_asset = 1
        ) t	
    {cond}""".format(
            cond=cond,
            import_taxes_and_charges="Import Zero Rated",
            export_taxes_and_charges="Export Zero Rated",
        ),
        tuple(vouchers),
    )
    return [d[0] for d in filtered]


COLUMNS = [
    {
        "fieldname": "section",
        "label": "section",
        "fieldtype": "Data",
        "width": 200,
    },
    # {
    #     "fieldname": "new_section",
    #     "label": "new_section",
    #     "fieldtype": "Data",
    #     "width": 200,
    # },
    {
        "fieldname": "is_fixed_asset",
        "label": "is_fixed_asset",
        "fieldtype": "Int",
        "width": 100,
    },
    {
        "fieldname": "taxes_and_charges",
        "label": "taxes_and_charges",
        "fieldtype": "Data",
        "width": 300,
    },
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
