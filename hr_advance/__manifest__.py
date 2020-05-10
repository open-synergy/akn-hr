# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Employee Cash Advance",
    "version": "11.0.0.4.0",
    "author": "Arkana, PT. Simetri Sinergi Indonesia",
    "depends": [
        "hr_contract",
        "project",
        "base_automation",
        "account",
        "base_tier_validation",
    ],
    "data": [
        "security/ir_module_category_data.xml",
        "security/res_groups_data.xml",
        "security/ir.model.access.csv",
        "data/base_automation_data.xml",
        "menu.xml",
        "wizards/hr_change_advance_amount_manual_views.xml",
        "wizards/hr_approve_advance_detail_views.xml",
        "wizards/hr_approve_advance_settlement_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_advance_type_views.xml",
        "views/hr_advance_settlement_type_views.xml",
        "views/hr_advance_views.xml",
        "views/hr_advance_settlement_views.xml",
    ],
    "demo": [
        "demo/product_category_demo.xml",
        "demo/account_journal_demo.xml",
        "demo/account_account_demo.xml",
        "demo/hr_advance_type_demo.xml",
        "demo/hr_advance_settlement_type_demo.xml",
    ],
    "installable": True,
    "application": True,
}
