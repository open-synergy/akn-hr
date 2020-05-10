# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrTravelRequestFixedExpense(models.Model):
    _name = "hr.travel_request_fixed_expense"
    _description = "Travel Request Fixed Expense"

    @api.depends(
        "approve_quantity",
        "approve_price_unit",
    )
    @api.multi
    def _compute_price_subtotal(self):
        for document in self:
            document.price_subtotal = document.approve_quantity * \
                document.approve_price_unit

    request_id = fields.Many2one(
        string="# Travel Request",
        comodel_name="hr.travel_request",
        ondelete="cascade",
    )
    pricelist_id = fields.Many2one(
        string="Pricelist",
        comodel_name="product.pricelist",
        required=True,
    )
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        related="request_id.employee_id",
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
    approve_price_unit = fields.Float(
        string="Approved Price Unit",
        readonly=True,
    )
    quantity = fields.Float(
        string="Qty",
        required=True,
        default=1.0,
    )
    approve_quantity = fields.Float(
        string="Approve Qty",
        readonly=True,
    )
    uom_id = fields.Many2one(
        string="UoM",
        comodel_name="product.uom",
        related="product_id.uom_id",
        store=True,
        readonly=True,
    )
    price_subtotal = fields.Float(
        string="Subtotal",
        compute="_compute_price_subtotal",
        store=True,
    )
    realization_method_id = fields.Many2one(
        string="Realization Method",
        comodel_name="hr.travel_request_realization_method",
        required=True,
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="hr.travel_request_type",
        related="request_id.type_id",
        store=False,
    )

    @api.onchange(
        "price_unit",
    )
    def onchange_approve_price_unit(self):
        self.approve_price_unit = self.price_unit

    @api.onchange(
        "quantity",
    )
    def onchange_approve_quantity(self):
        self.approve_quantity = self.quantity

    @api.onchange(
        "product_id",
        "pricelist_id",
        "approve_quantity",
    )
    def onchange_price_unit(self):
        result = 0.0
        if self.product_id and \
                self.pricelist_id:
            result = self.pricelist_id.get_product_price(
                product=self.product_id,
                quantity=self.approve_quantity,
                partner=False,
                date=False,
                uom_id=False,
            )
        self.price_unit = result
