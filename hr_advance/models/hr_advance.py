# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrAdvance(models.Model):
    _name = "hr.advance"
    _description = "Employee Advance"
    _inherit = [
        "mail.thread",
    ]

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    @api.depends(
        "line_ids",
        "line_ids.price_subtotal",
    )
    @api.multi
    def _compute_amount_total(self):
        for document in self:
            total = 0.0
            for line in document.line_ids:
                total += line.price_subtotal
            document.amount_total = total

    @api.depends(
        "move_line_id.amount_residual",
        "move_line_id",
        "amount_total",
        "state",
    )
    @api.multi
    def _compute_residual(self):
        for document in self:
            realized = 0.0
            residual = document.amount_total
            if document.move_line_id:
                residual = -1.0 * document.move_line_id.amount_residual
                realized = document.amount_total - residual
            document.amount_realized = realized
            document.amount_residual = residual

    name = fields.Char(
        string="# Document",
        default="/",
        required=True,
        copy=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self._default_company_id(),
    )
    project_id = fields.Many2one(
        string="Project",
        comodel_name="project.project",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_request = fields.Date(
        string="Date Request",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    amount_total = fields.Float(
        string="Total",
        compute="_compute_amount_total",
        store=True,
    )
    amount_realized = fields.Float(
        string="Total Realized",
        compute="_compute_residual",
        store=True,
    )
    amount_residual = fields.Float(
        string="Total Residual",
        compute="_compute_residual",
        store=True,
    )

    # Accounting Setting
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        domain=[
            ("type", "=", "general"),
        ],
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    advance_payable_account_id = fields.Many2one(
        string="Employee Advance Payable Account",
        comodel_name="account.account",
        domain=[
            ("reconcile", "=", True),
        ],
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    move_id = fields.Many2one(
        string="# Move",
        comodel_name="account.move",
        readonly=True,
    )
    move_line_id = fields.Many2one(
        string="Account Move Line",
        comodel_name="account.move.line",
        readonly=True,
    )
    line_ids = fields.One2many(
        string="Advance Details",
        comodel_name="hr.advance_line",
        inverse_name="advance_id",
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("approve", "Waiting for Realization"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        required=True,
        readonly=True,
    )

    @api.multi
    def action_confirm(self):
        for document in self:
            document.write(document._prepare_confirm_data())

    @api.multi
    def action_approve(self):
        for document in self:
            document.write(document._prepare_approve_data())
            document._create_account_move()

    @api.multi
    def action_done(self):
        for document in self:
            document.write(document._prepare_done_data())

    @api.multi
    def action_cancel(self):
        for document in self:
            move = document.move_id
            document.write(document._prepare_cancel_data())
            if move:
                move.unlink()

    @api.multi
    def action_restart(self):
        for document in self:
            document.write(document._prepare_restart_data())

    @api.multi
    def _prepare_confirm_data(self):
        self.ensure_one()
        return {
            "state": "confirm",
            "confirm_date": fields.Datetime.now(),
            "confirm_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_approve_data(self):
        self.ensure_one()
        return {
            "state": "approve",
            "approve_date": fields.Datetime.now(),
            "approve_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_done_data(self):
        self.ensure_one()
        return {
            "state": "done",
            "done_date": fields.Datetime.now(),
            "done_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        return {
            "state": "cancel",
            "cancel_date": fields.Datetime.now(),
            "cancel_user_id": self.env.user.id,
            "move_id": False,
            "move_line_id": False,
        }

    @api.multi
    def _prepare_restart_data(self):
        self.ensure_one()
        return {
            "state": "draft",
            "confirm_date": False,
            "confirm_user_id": False,
            "approve_date": False,
            "approve_user_id": False,
            "done_date": False,
            "done_user_id": False,
            "cancel_date": False,
            "cancel_user_id": False,
        }

    @api.multi
    def _create_account_move(self):
        self.ensure_one()
        obj_move = self.env["account.move"]
        obj_line = self.env["account.move.line"]
        move = obj_move.create(self._prepare_account_move())
        self.write({"move_id": move.id})
        ctx = {
            "check_move_validity": False,
        }
        header_move_line = obj_line.with_context(ctx).create(
            self._prepare_header_account_move_lines())
        self.write({"move_line_id": header_move_line.id})
        for line in self.line_ids:
            line._create_account_move_line()

    @api.multi
    def _prepare_account_move(self):
        self.ensure_one()
        return {
            "date": fields.Date.today(),
            "journal_id": self.journal_id.id,
            "name": "/",
        }

    @api.multi
    def _prepare_header_account_move_lines(self):
        self.ensure_one()
        aa = self.project_id.analytic_account_id
        return {
            "move_id": self.move_id.id,
            "partner_id": self._get_partner().id,
            "account_id": self.advance_payable_account_id.id,
            "analytic_account_id": aa and aa.id or False,
            "debit": 0.0,
            "credit": self.amount_total,

        }

    @api.multi
    def _get_partner(self):
        self.ensure_one()
        if not self.employee_id.address_home_id:
            err_msg = _("No home address defined for employee")
            raise UserError(err_msg)
        return self.employee_id.address_home_id
