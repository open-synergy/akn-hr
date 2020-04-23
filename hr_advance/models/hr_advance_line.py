# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrAdvanceLine(models.Model):
    _name = "hr.advance_line"
    _description = "Employee Advance Detail"

    @api.depends(
        "quantity",
        "price_unit",
    )
    @api.multi
    def _compute_price_subtotal(self):
        for document in self:
            document.price_subtotal = document.quantity * \
                document.price_unit

    @api.depends(
        "product_id",
    )
    @api.multi
    def _compute_allowed_uom_ids(self):
        obj_uom = self.env["product.uom"]
        for document in self:
            result = []
            if document.product_id:
                categ = document.product_id.uom_id.category_id
                criteria = [
                    ("category_id", "=", categ.id),
                ]
                result = obj_uom.search(criteria).ids
            document.allowed_uom_ids = result

    advance_id = fields.Many2one(
        string="# Advance",
        comodel_name="hr.advance",
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
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
        required=True,
    )
    price_unit = fields.Float(
        string="Unit Price",
        required=True,
    )
    quantity = fields.Float(
        string="Qty",
        required=True,
        default=1.0,
    )
    allowed_uom_ids = fields.Many2many(
        string="Allowed UoM",
        comodel_name="product.uom",
        compute="_compute_allowed_uom_ids",
        store=False,
    )
    uom_id = fields.Many2one(
        string="UoM",
        comodel_name="product.uom",
        required=True,
    )
    price_subtotal = fields.Float(
        string="Subtotal",
        compute="_compute_price_subtotal",
        store=True,
    )

    @api.multi
    def _create_account_move_line(self):
        self.ensure_one()
        obj_line = self.env["account.move.line"]
        ctx = {
            "check_move_validity": False,
        }
        obj_line.with_context(ctx).create(
            self._prepare_account_move_line())

    @api.multi
    def _prepare_account_move_line(self):
        self.ensure_one()
        aa = self.advance_id.project_id.analytic_account_id
        return {
            "move_id": self.advance_id.move_id.id,
            "partner_id": self.advance_id._get_partner().id,
            "account_id": self.account_id.id,
            "analytic_account_id": aa and aa.id or False,
            "credit": 0.0,
            "debit": self.price_subtotal,
        }

    @api.onchange(
        "product_id",
    )
    def onchange_uom_id(self):
        self.uom_id = False
        if self.product_id:
            self.uom_id = self.product_id.uom_id
