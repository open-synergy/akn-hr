# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrApproveDailyExpense(models.TransientModel):
    _name = "hr.approve_daily_expense"
    _description = "Approved Daily Expense"

    @api.model
    def _default_request_id(self):
        return self.env.context.get("active_id", False)

    request_id = fields.Many2one(
        string="# Request",
        comodel_name="hr.travel_request",
        default=lambda self: self._default_request_id(),
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="request_id.currency_id",
        readonly=True,
    )
    line_ids = fields.One2many(
        string="Details",
        comodel_name="hr.approve_daily_expense_line",
        inverse_name="wizard_id",
    )

    @api.onchange(
        "request_id",
    )
    def onchange_line_ids(self):
        result = []
        if self.request_id:
            for line in self.request_id.daily_expense_ids:
                result.append((0, 0, {
                    "line_id": line.id,
                    "final_price_unit": line.price_unit,
                }))
            self.update({"line_ids": result})

    @api.multi
    def action_confirm(self):
        for document in self:
            document._update_amount()

    @api.multi
    def _update_amount(self):
        self.ensure_one()
        self.request_id.restart_validation()
        for line in self.line_ids:
            line.line_id.write({
                "final_price_unit": line.final_price_unit,
            })


class HrApproveDailyExpenseLine(models.TransientModel):
    _name = "hr.approve_daily_expense_line"
    _description = "Approved Daily Expense Line"

    wizard_id = fields.Many2one(
        string="Wizard",
        comodel_name="hr.approve_daily_expense",
        ondelete="cascade",
    )
    line_id = fields.Many2one(
        string="Daily Expense Line",
        comodel_name="hr.travel_request_daily_expense",
        ondelete="cascade",
        readonly=True,
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        related="line_id.product_id",
        readonly=True,
        store=False,
    )
    price_unit = fields.Float(
        string="Unit Price",
        related="line_id.price_unit",
        store=False,
        readonly=True,
    )
    final_price_unit = fields.Float(
        string="Approved Price Unit",
        required=True,
    )
