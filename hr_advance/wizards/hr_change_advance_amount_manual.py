# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrChangeAdvanceAmountManual(models.TransientModel):
    _name = "hr.change_advance_amount_manual"
    _description = "Change Approved Amount Manual"

    @api.model
    def _default_advance_id(self):
        return self.env.context.get("active_id", False)

    advance_id = fields.Many2one(
        string="# Advance",
        comodel_name="hr.advance",
        default=lambda self: self._default_advance_id(),
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="advance_id.currency_id",
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
        "advance_id",
    )
    def onchange_amount_requested(self):
        self.amount_requested = self.advance_id.amount_manual

    @api.onchange(
        "advance_id",
    )
    def onchange_amount_approved(self):
        self.amount_approved = self.advance_id.amount_manual

    @api.multi
    def action_confirm(self):
        for document in self:
            document._update_amount()

    @api.multi
    def _update_amount(self):
        self.ensure_one()
        self.advance_id.write({
            "final_amount_manual": self.amount_approved,
        })
