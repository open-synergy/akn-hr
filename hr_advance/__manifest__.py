# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Travel Request",
    "version": "11.0.0.0.0",
    "summary": "Custom Travel Request Form for PT Indoturbine",
    "author": "Arkana, PT. Simetri Sinergi Indonesia",
    "description": """
Features :
- Travel Advance Request
- Travel Expense Realization
    """,
    "depends": [
        "hr_contract",
        "project",
        "base_automation",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/base_automation_data.xml",
        "menu.xml",
        "views/hr_advance_views.xml",
    ],
    "installable": True
}
