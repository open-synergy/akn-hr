# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrTravelRequestType(models.Model):
    _name = "hr.travel_request_type"
    _description = "Employee Travel Request Type"

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
    note = fields.Text(
        string="Note",
    )
    sequence_id = fields.Many2one(
        string="Sequence",
        comodel_name="ir.sequence",
        company_dependent=True,
    )
    transportation_expense_ids = fields.One2many(
        string="Transportation Expenses",
        comodel_name="hr.travel_request_type_transportation_expense",
        inverse_name="type_id",
    )
    daily_expense_ids = fields.One2many(
        string="Daily Expenses",
        comodel_name="hr.travel_request_type_daily_expense",
        inverse_name="type_id",
    )
    fixed_expense_ids = fields.One2many(
        string="Fixed Expenses",
        comodel_name="hr.travel_request_type_fixed_expense",
        inverse_name="type_id",
    )
    allowed_realization_method_ids = fields.Many2many(
        string="Allowed Realization Methods",
        comodel_name="hr.travel_request_realization_method",
        relation="rel_travel_request_type_2_realization_method",
        column1="type_id",
        column2="realization_method_id",
    )
