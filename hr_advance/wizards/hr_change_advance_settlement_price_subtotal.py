# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrChangeAdvanceSettlementPriceSubtotal(models.TransientModel):
    _name = "hr.change_advance_settlement_price_subtotal"
    _description = "Change Approved Settlement Price Subtotal"

    @api.model
    def _default_settlement_id(self):
        return self.env.context.get("active_id", False)

    settlement_id = fields.Many2one(
        string="# Settlement",
        comodel_name="hr.advance_settlement",
        default=lambda self: self._default_settlement_id(),
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="settlement_id.currency_id",
        readonly=True,
    )
    line_ids = fields.One2many(
        string="Details",
        comodel_name="hr.change_advance_settlement_line_price_subtotal",
        inverse_name="wizard_id",
    )

    @api.onchange(
        "settlement_id",
    )
    def onchange_line_ids(self):
        result = []
        if self.settlement_id:
            for line in self.settlement_id.line_ids:
                result.append((0, 0, {
                    "line_id": line.id,
                    "final_price_subtotal": line.price_subtotal,
                }))
            self.update({"line_ids": result})

    @api.multi
    def action_confirm(self):
        for document in self:
            document._update_amount()

    @api.multi
    def _update_amount(self):
        self.ensure_one()
        self.settlement_id.restart_validation()
        for line in self.line_ids:
            line.line_id.write({
                "final_price_subtotal": line.final_price_subtotal,
            })


class HrChangeAdvanceSettlementLinePriceSubtotal(models.TransientModel):
    _name = "hr.change_advance_settlement_line_price_subtotal"
    _description = "Change Approved Settlement Line Price Subtotal"

    wizard_id = fields.Many2one(
        string="Wizard",
        comodel_name="change_advance_settlement_price_subtotal",
        ondelete="cascade",
    )
    line_id = fields.Many2one(
        string="Settlement Line",
        comodel_name="hr.advance_settlement_line",
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
    quantity = fields.Float(
        string="Qty",
        related="line_id.quantity",
        store=False,
        readonly=True,
    )
    uom_id = fields.Many2one(
        string="UoM",
        comodel_name="product.uom",
        related="line_id.uom_id",
        store=False,
        readonly=True,
    )
    price_subtotal = fields.Float(
        string="Subtotal",
        related="line_id.price_subtotal",
        store=False,
        readonly=True,
    )
    final_price_subtotal = fields.Float(
        string="Approved Subtotal",
        required=True,
    )
