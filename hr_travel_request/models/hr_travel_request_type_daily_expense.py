# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrTravelRequestTypeDailyExpense(models.Model):
    _name = "hr.travel_request_type_daily_expense"
    _description = "Travel Request Type Daily Expense"

    type_id = fields.Many2one(
        string="Travel Request Type",
        comodel_name="hr.travel_request_type",
        ondelete="cascade",
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        required=True,
    )
    quantity = fields.Float(
        string="Qty",
        required=True,
        default=1.0,
    )
    uom_id = fields.Many2one(
        string="UoM",
        comodel_name="product.uom",
        related="product_id.uom_id",
        store=True,
        readonly=True,
    )
    realization_method_id = fields.Many2one(
        string="Realization Method",
        comodel_name="hr.travel_request_realization_method",
        required=True,
    )
