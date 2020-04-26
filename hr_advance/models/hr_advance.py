# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrAdvance(models.Model):
    _name = "hr.advance"
    _description = "Employee Advance Request"
    _inherit = [
        "mail.thread",
        "tier.validation",
    ]
    _state_from = ["draft", "confirm"]
    _state_to = ["approve"]

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    @api.model
    def _default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    @api.model
    def _default_employee_id(self):
        employees = self.env.user.employee_ids
        if len(employees) > 0:
            return employees[0].id

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
        "employee_advance_payable_move_line_id.amount_residual",
        "employee_advance_payable_move_line_id",
        "amount_total",
        "state",
    )
    @api.multi
    def _compute_residual(self):
        for document in self:
            realized = 0.0
            residual = document.amount_total
            if document.employee_advance_payable_move_line_id:
                move_line = document.employee_advance_payable_move_line_id
                residual = -1.0 * move_line.amount_residual
                realized = document.amount_total - residual
            document.amount_realized = realized
            document.amount_residual = residual

    @api.depends(
        "employee_advance_move_line_id.amount_residual",
        "employee_advance_move_line_id",
        "state",
    )
    @api.multi
    def _compute_settlement(self):
        for document in self:
            settled = 0.0
            due = document.amount_total
            if document.employee_advance_move_line_id:
                move_line = document.employee_advance_move_line_id
                due = 1.0 * move_line.amount_residual
                settled = document.amount_total - due
            document.amount_due = due
            document.amount_settled = settled

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
        required=False,
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
        default=lambda self: self._default_currency_id(),
        required=False,
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
        default=lambda self: self._default_employee_id(),
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="hr.advance_type",
        required=True,
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
    amount_total = fields.Monetary(
        string="Total",
        compute="_compute_amount_total",
        store=True,
    )
    amount_realized = fields.Monetary(
        string="Total Realized",
        compute="_compute_residual",
        store=True,
    )
    amount_residual = fields.Monetary(
        string="Total Residual",
        compute="_compute_residual",
        store=True,
    )
    amount_settled = fields.Monetary(
        string="Total Settlement",
        compute="_compute_settlement",
        store=True,
    )
    amount_due = fields.Monetary(
        string="Total Due",
        compute="_compute_settlement",
        store=True,
    )
    note = fields.Text(
        string="Note",
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
    employee_advance_payable_account_id = fields.Many2one(
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
    employee_advance_account_id = fields.Many2one(
        string="Employee Advance Account",
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
        copy=False,
    )
    employee_advance_payable_move_line_id = fields.Many2one(
        string="Employee Advance Payable Move Line",
        comodel_name="account.move.line",
        readonly=True,
        copy=False,
    )
    employee_advance_move_line_id = fields.Many2one(
        string="Employee Advance Move Line",
        comodel_name="account.move.line",
        readonly=True,
        copy=False,
    )
    line_ids = fields.One2many(
        string="Advance Details",
        comodel_name="hr.advance_line",
        inverse_name="advance_id",
        copy=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("approve", "Waiting for Realization"),
            ("open", "Waiting for Settlement"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        copy=False,
        default="draft",
        required=True,
        readonly=True,
    )
    # Log Fields
    confirm_date = fields.Datetime(
        string="Confirm Date",
        readonly=True,
        copy=False,
    )
    confirm_user_id = fields.Many2one(
        string="Confirmed By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    approve_date = fields.Datetime(
        string="Approve Date",
        readonly=True,
        copy=False,
    )
    approve_user_id = fields.Many2one(
        string="Approve By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    open_user_id = fields.Many2one(
        string="Open By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    open_date = fields.Datetime(
        string="Open Date",
        readonly=True,
        copy=False,
    )
    done_date = fields.Datetime(
        string="Finish Date",
        readonly=True,
        copy=False,
    )
    done_user_id = fields.Many2one(
        string="Finished By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    cancel_date = fields.Datetime(
        string="Cancel Date",
        readonly=True,
        copy=False,
    )
    cancel_user_id = fields.Many2one(
        string="Cancelled By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )

    @api.multi
    def action_confirm(self):
        for document in self:
            document.write(document._prepare_confirm_data())

    @api.multi
    def action_approve(self):
        for document in self:
            document.write(document._prepare_approve_data())
            document._create_accounting_entry()

    @api.multi
    def action_open(self):
        for document in self:
            document.write(document._prepare_open_data())

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
            document.restart_validation()

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
    def _prepare_open_data(self):
        self.ensure_one()
        return {
            "state": "open",
            "open_date": fields.Datetime.now(),
            "open_user_id": self.env.user.id,
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
    def _create_accounting_entry(self):
        self.ensure_one()
        self._create_account_move()
        self._create_payable_advance_move_line()
        self._create_advance_move_line()

    @api.multi
    def _create_account_move(self):
        self.ensure_one()
        obj_move = self.env["account.move"]
        move = obj_move.create(self._prepare_account_move())
        self.write({"move_id": move.id})

    @api.multi
    def _create_payable_advance_move_line(self):
        self.ensure_one()
        obj_line = self.env["account.move.line"]
        ctx = {
            "check_move_validity": False,
        }
        line = obj_line.with_context(ctx).create(
            self._prepare_payable_advance_move_lines())
        self.write({
            "employee_advance_payable_move_line_id": line.id})

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
            "employee_advance_move_line_id": line.id})

    @api.multi
    def _prepare_account_move(self):
        self.ensure_one()
        return {
            "date": fields.Date.today(),
            "journal_id": self.journal_id.id,
            "name": "/",
        }

    @api.multi
    def _get_analytic_account(self):
        self.ensure_one()
        result = False
        project = self.project_id
        if project:
            result = project.analytic_account_id
        return result

    @api.multi
    def _prepare_advance_move_lines(self):
        self.ensure_one()
        aa = self._get_analytic_account()
        return {
            "move_id": self.move_id.id,
            "partner_id": self._get_partner().id,
            "account_id": self.employee_advance_account_id.id,
            "analytic_account_id": aa and aa.id or False,
            "credit": 0.0,
            "debit": self.amount_total,
        }

    @api.multi
    def _prepare_payable_advance_move_lines(self):
        self.ensure_one()
        aa = self._get_analytic_account()
        return {
            "move_id": self.move_id.id,
            "partner_id": self._get_partner().id,
            "account_id": self.employee_advance_payable_account_id.id,
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

    @api.onchange(
        "type_id",
    )
    def onchange_journal_id(self):
        self.journal_id = False
        if self.type_id:
            self.journal_id = self.type_id.journal_id

    @api.onchange(
        "type_id",
        "employee_id",
    )
    def onchange_employee_advance_payable_account_id(self):
        result = False
        if self.employee_id:
            result = self.employee_id.employee_advance_payable_account_id

        if not result and self.type_id:
            result = self.type_id.employee_advance_payable_account_id

        self.employee_advance_payable_account_id = result

    @api.onchange(
        "type_id",
        "employee_id",
    )
    def onchange_employee_advance_account_id(self):
        result = False
        if self.employee_id:
            result = self.employee_id.employee_advance_account_id

        if not result and self.type_id:
            result = self.type_id.employee_advance_account_id

        self.employee_advance_account_id = result

    @api.multi
    def unlink(self):
        strWarning = _("You can only delete data on draft state")
        for document in self:
            if document.state != "draft":
                if not self.env.context.get("force_unlink", False):
                    raise UserError(strWarning)
        _super = super(HrAdvance, self)
        _super.unlink()

    @api.multi
    def validate_tier(self):
        _super = super(HrAdvance, self)
        _super.validate_tier()
        for document in self:
            if document.validated:
                document.action_approve()
