# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrTravelRequestRealizationMethod(models.Model):
    _name = "hr.travel_request_realization_method"
    _description = "Employee Travel Request Realization Method"

    name = fields.Char(
        string="Travel Request Type",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    confirm_method = fields.Char(
        string="Confirm Method",
    )
    approve_method = fields.Char(
        string="Approve Method",
    )
    cancel_method = fields.Char(
        string="Cancel Method",
    )
    restart_method = fields.Char(
        string="Restart Method",
    )
    note = fields.Text(
        string="Note",
    )
