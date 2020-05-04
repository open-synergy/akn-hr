# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrAdvanceSettlementLine(models.Model):
    _name = "hr.advance_settlement_line"
    _description = "Employee Advance Settlement Line"

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

    settlement_id = fields.Many2one(
        string="# Settlement",
        comodel_name="hr.advance_settlement",
    )
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        related="settlement_id.employee_id",
        store=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
    )
    date = fields.Date(
        string="Date",
        required=True,
    )
    advance_id = fields.Many2one(
        string="# Advance",
        comodel_name="hr.advance",
        required=True,
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
    final_price_subtotal = fields.Float(
        string="Approved Subtotal",
        readonly=True,
    )
    move_id = fields.Many2one(
        string="# Expense Move",
        comodel_name="account.move",
        readonly=True,
    )
    employee_advance_move_line_id = fields.Many2one(
        string="Employee Advance Move Line",
        comodel_name="account.move.line",
        readonly=True,
    )

    @api.multi
    def _create_accounting_entry(self):
        self.ensure_one()
        self._create_account_move()
        self._create_advance_move_line()
        self._create_expense_move_line()

    @api.multi
    def _create_account_move(self):
        self.ensure_one()
        obj_move = self.env["account.move"]
        move = obj_move.create(self._prepare_account_move())
        self.write({"move_id": move.id})

    @api.multi
    def _prepare_account_move(self):
        self.ensure_one()
        return {
            "date": self.date,
            "journal_id": self.settlement_id.journal_id.id,
            "name": "/",
        }

    @api.multi
    def _get_currency(self):
        self.ensure_one()
        result = False
        if self.advance_id.company_id.currency_id != self.settlement_id.currency_id:
            result = self.settlement_id.currency_id
        return result

    @api.multi
    def _prepare_expense_move_lines(self):
        self.ensure_one()
        aa = self._get_analytic_account()
        debit, credit, amount_currency = self._get_expense_amount()
        currency = self._get_currency()
        return {
            "move_id": self.move_id.id,
            "partner_id": self._get_partner().id,
            "account_id": self.account_id.id,
            "analytic_account_id": aa and aa.id or False,
            "debit": debit,
            "credit": credit,
            "currency_id": currency and currency.id or False,
            "amount_currency": amount_currency,
        }

    @api.multi
    def _prepare_advance_move_lines(self):
        self.ensure_one()
        debit, credit, amount_currency = self._get_advance_amount()
        employee_advance_account = self.advance_id.employee_advance_account_id
        currency = self._get_currency()
        return {
            "move_id": self.move_id.id,
            "partner_id": self._get_partner().id,
            "account_id": employee_advance_account.id,
            "debit": debit,
            "credit": credit,
            "currency_id": currency and currency.id or False,
            "amount_currency": amount_currency,
        }

    @api.multi
    def _get_expense_amount(self):
        debit = credit = amount = amount_currency = 0.0
        currency = self._get_currency()

        if currency:
            amount_currency = self.final_price_subtotal
            amount = currency.with_context(date=self.date).compute(
                amount_currency,
                self.settlement_id.company_id.currency_id,
            )
        else:
            amount = self.final_price_subtotal

        if amount >= 0.0:
            debit = amount
        else:
            credit = amount

        return debit, credit, amount_currency

    @api.multi
    def _get_advance_amount(self):
        debit = credit = amount_currency = 0.0
        currency = self._get_currency()

        if currency:
            amount_currency = self.final_price_subtotal
            amount = currency.with_context(date=self.date).compute(
                amount_currency,
                self.settlement_id.company_id.currency_id,
            )
        else:
            amount = self.final_price_subtotal

        if amount >= 0.0:
            credit = amount
            amount_currency *= -1.0
        else:
            debit = amount

        return debit, credit, amount_currency

    @api.multi
    def _get_analytic_account(self):
        self.ensure_one()
        result = False
        project = self.advance_id.project_id
        if project:
            result = project.analytic_account_id
        return result

    @api.multi
    def _create_advance_move_line(self):
        self.ensure_one()
        obj_line = self.env["account.move.line"]
        ctx = {
            "check_move_validity": False,
        }
        line = obj_line.with_context(ctx).create(
            self._prepare_advance_move_lines())
        self.write({
            "employee_advance_move_line_id": line.id,
        })

    @api.multi
    def _create_expense_move_line(self):
        self.ensure_one()
        obj_line = self.env["account.move.line"]
        ctx = {
            "check_move_validity": False,
        }
        obj_line.with_context(ctx).create(
            self._prepare_expense_move_lines())

    @api.multi
    def _get_partner(self):
        self.ensure_one()
        if not self.settlement_id.employee_id.address_home_id:
            err_msg = _("No home address defined for employee")
            raise UserError(err_msg)
        return self.settlement_id.employee_id.address_home_id

    @api.multi
    def _reconcile_advance(self):
        self.ensure_one()
        lines = self.employee_advance_move_line_id + \
            self.advance_id.employee_advance_move_line_id

        lines.reconcile()

    @api.onchange(
        "product_id",
    )
    def onchange_uom_id(self):
        self.uom_id = False
        if self.product_id:
            self.uom_id = self.product_id.uom_id

    @api.onchange(
        "product_id",
    )
    def onchange_account_id(self):
        result = False
        if self.product_id:
            result = self.product_id.property_account_expense_id

        if not result and \
                self.product_id:
            result = self.product_id.categ_id.property_account_expense_categ_id

        self.account_id = result

    @api.onchange(
        "price_unit",
        "quantity",
    )
    def onchange_final_price_subtotal(self):
        self.final_price_subtotal = self.price_subtotal

    @api.multi
    def _unlink_account_move(self):
        self.ensure_one()
        move = self.move_id
        self.employee_advance_move_line_id.remove_move_reconcile()
        self.write({"move_id": False})
        move.unlink()
