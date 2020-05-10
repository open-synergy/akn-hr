# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Employee Travel Request",
    "version": "11.0.0.1.0",
    "author": "Arkana, PT. Simetri Sinergi Indonesia",
    "license": "LGPL-3",
    "depends": [
        "hr_contract",
        "project",
        "base_automation",
        "account",
        "base_tier_validation",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/hr_travel_request_realization_method_data.xml",
        "menu.xml",
        "wizards/hr_approve_transportation_expense_views.xml",
        "wizards/hr_approve_daily_expense_views.xml",
        "wizards/hr_approve_fixed_expense_views.xml",
        "views/hr_travel_request_type_views.xml",
        "views/hr_travel_request_realization_method_views.xml",
        "views/hr_travel_request_views.xml",
    ],
    "demo": [
        "demo/travel_request_type_demo.xml",
    ],
    "installable": True,
    "application": True,
}
