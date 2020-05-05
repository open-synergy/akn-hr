# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrTravelRequestTransportationExpense(models.Model):
    _name = "hr.travel_request_transportation_expense"
    _description = "Travel Request Transportation Expense"

    @api.depends(
        "final_quantity",
        "final_price_unit",
    )
    @api.multi
    def _compute_price_subtotal(self):
        for document in self:
            document.price_subtotal = document.final_quantity * \
                document.final_price_unit

    @api.depends(
        "round_trip",
        "quantity",
    )
    @api.multi
    def _compute_final_qty(self):
        for document in self:
            result = document.quantity
            if document.round_trip:
                result *= 2
            document.final_quantity = result

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
    round_trip = fields.Boolean(
        string="Round Trip",
        default=False,
    )
    price_unit = fields.Float(
        string="Unit Price",
        required=True,
    )
    final_price_unit = fields.Float(
        string="Approved Price Unit",
        readonly=True,
    )
    quantity = fields.Float(
        string="Qty",
        required=True,
        default=1.0,
    )
    final_quantity = fields.Float(
        string="Final Qty.",
        compute="_compute_final_qty",
        store=True,
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
    realization_method = fields.Selection(
        string="Realization Method",
        selection=[
            ("manual", "Manual Procurement"),
        ],
        required=True,
        default="manual",
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
    def onchange_final_price_unit(self):
        self.final_price_unit = self.price_unit

    @api.onchange(
        "product_id",
        "pricelist_id",
        "final_quantity",
    )
    def onchange_price_unit(self):
        result = 0.0
        if self.product_id and \
                self.pricelist_id:
            result = self.pricelist_id.get_product_price(
                product=self.product_id,
                quantity=self.final_quantity,
                partner=False,
                date=False,
                uom_id=False,
            )
        self.price_unit = result
