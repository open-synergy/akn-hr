# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrAdvanceSettlement(models.Model):
    _name = "hr.advance_settlement"
    _description = "Employee Advance Realization"
    _inherit = [
        "mail.thread",
        "tier.validation",
    ]
    _state_from = ["draft", "confirm"]
    _state_to = ["done"]

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
        copy=True,
        required=True,
        default=lambda self: self._default_company_id(),
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        default=lambda self: self._default_currency_id(),
        copy=True,
        required=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="hr.advance_settlement_type",
        copy=True,
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
        default=lambda self: self._default_employee_id(),
        copy=True,
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    line_ids = fields.One2many(
        string="Realization Details",
        comodel_name="hr.advance_settlement_line",
        inverse_name="settlement_id",
        copy=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    # Accounting Setting
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        domain=[
            ("type", "=", "general"),
        ],
        copy=True,
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
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        copy=False,
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
    def action_cancel(self):
        for document in self:
            document.write(document._prepare_cancel_data())
            document._unlink_accounting_entry()

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
            "state": "done",
            "approve_date": fields.Datetime.now(),
            "approve_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        return {
            "state": "cancel",
            "cancel_date": fields.Datetime.now(),
            "cancel_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_restart_data(self):
        self.ensure_one()
        return {
            "state": "draft",
            "confirm_date": False,
            "confirm_user_id": False,
            "done_date": False,
            "done_user_id": False,
            "cancel_date": False,
            "cancel_user_id": False,
        }

    @api.multi
    def _create_accounting_entry(self):
        self.ensure_one()
        for line in self.line_ids.filtered(lambda r: not r.move_id):
            line._create_accounting_entry()
            line._reconcile_advance()

    @api.multi
    def _unlink_accounting_entry(self):
        self.ensure_one()
        for line in self.line_ids:
            line._unlink_account_move()

    @api.onchange(
        "type_id",
    )
    def onchange_journal_id(self):
        self.journal_id = False
        if self.type_id:
            self.journal_id = self.type_id.journal_id

    @api.multi
    def unlink(self):
        strWarning = _("You can only delete data on draft state")
        for document in self:
            if document.state != "draft":
                if not self.env.context.get("force_unlink", False):
                    raise UserError(strWarning)
        _super = super(HrAdvanceSettlement, self)
        _super.unlink()

    @api.multi
    def validate_tier(self):
        _super = super(HrAdvanceSettlement, self)
        _super.validate_tier()
        for document in self:
            if document.validated:
                document.action_approve()
