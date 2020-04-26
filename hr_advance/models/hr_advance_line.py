# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrAdvanceLine(models.Model):
    _name = "hr.advance_line"
    _description = "Employee Advance Request Line"

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
        ondelete="cascade",
    )
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        related="advance_id.employee_id",
        store=True,
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
    type_id = fields.Many2one(
        string="Type",
        comodel_name="hr.advance_type",
        related="advance_id.type_id",
        store=False,
    )

    @api.onchange(
        "product_id",
    )
    def onchange_uom_id(self):
        self.uom_id = False
        if self.product_id:
            self.uom_id = self.product_id.uom_id
