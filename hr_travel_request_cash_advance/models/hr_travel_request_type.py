# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrTravelRequestType(models.Model):
    _name = "hr.travel_request_type"
    _inherit = "hr.travel_request_type"

    cash_advance_type_id = fields.Many2one(
        string="Cash Advance Type",
        comodel_name="hr.advance_type",
    )
