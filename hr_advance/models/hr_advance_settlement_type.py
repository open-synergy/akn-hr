# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrAdvanceSettlementType(models.Model):
    _name = "hr.advance_settlement_type"
    _description = "Employee Advance Realization Type"

    name = fields.Char(
        string="Employee Advance Realization Type",
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
    allowed_product_categ_ids = fields.Many2many(
        string="Allowed Product Categories",
        comodel_name="product.category",
        relation="rel_emp_advance_type_2_product_categ",
        column1="type_id",
        column2="category_id",
    )
    allowed_product_ids = fields.Many2many(
        string="Allowed Products",
        comodel_name="product.product",
        relation="rel_emp_advance_type_2_product",
        column1="type_id",
        column2="product_id",
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        company_dependent=True,
        domain=[
            ("type", "=", "general"),
        ],
    )
    sequence_id = fields.Many2one(
        string="Sequence",
        comodel_name="ir.sequence",
        company_dependent=True,
    )
