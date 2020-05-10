# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Employee Travel Request - Cash Advance Integration",
    "version": "11.0.0.0.0",
    "author": "Arkana, PT. Simetri Sinergi Indonesia",
    "license": "LGPL-3",
    "depends": [
        "hr_advance",
        "hr_travel_request",
    ],
    "data": [
        "data/hr_travel_request_realization_method_data.xml",
        "views/hr_travel_request_type_views.xml",
        "views/hr_travel_request_views.xml",
    ],
    "installable": True,
}
