# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrChangeAdvancePriceSubtotal(models.TransientModel):
    _name = "hr.change_advance_price_subtotal"
    _description = "Change Approved Price Subtotal"

    @api.model
    def _default_line_id(self):
        return self.env.context.get("active_id", False)

    line_id = fields.Many2one(
        string="Line Advance",
        comodel_name="hr.advance_line",
        default=lambda self: self._default_line_id(),
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="line_id.advance_id.currency_id",
        readonly=True,
    )
    amount_requested = fields.Monetary(
        string="Amount Requested",
        readonly=True,
    )
    amount_approved = fields.Monetary(
        string="Amount Approved",
        required=True,
    )

    @api.onchange(
        "line_id",
    )
    def onchange_amount_requested(self):
        self.amount_requested = self.line_id.price_subtotal

    @api.onchange(
        "line_id",
    )
    def onchange_amount_approved(self):
        self.amount_approved = self.line_id.price_subtotal

    @api.multi
    def action_confirm(self):
        for document in self:
            document._update_amount()

    @api.multi
    def _update_amount(self):
        self.ensure_one()
        self.line_id.write({
            "final_price_subtotal": self.amount_approved,
        })
