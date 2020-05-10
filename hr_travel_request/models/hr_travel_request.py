# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrTravelRequest(models.Model):
    _name = "hr.travel_request"
    _description = "Employee Travel Request"
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
        "date_arrive",
        "date_depart"
    )
    @api.multi
    def _compute_days_travel(self):
        for document in self:
            result = 0
            if document.date_arrive and document.date_depart:
                dt_date_depart = fields.Date.from_string(document.date_depart)
                dt_date_arrive = fields.Date.from_string(document.date_arrive)
                result = (dt_date_arrive - dt_date_depart).days
            document.days_travel = result

    @api.depends(
        "transportation_expense_ids",
        "transportation_expense_ids.price_subtotal",
    )
    @api.multi
    def _compute_amount_total_transportation(self):
        for document in self:
            total = 0.0
            for line in document.transportation_expense_ids:
                total += line.price_subtotal
            document.amount_total_transportation = total

    @api.depends(
        "daily_expense_ids",
        "daily_expense_ids.price_subtotal",
    )
    @api.multi
    def _compute_amount_total_daily(self):
        for document in self:
            total = 0.0
            for line in document.daily_expense_ids:
                total += line.price_subtotal
            document.amount_total_daily = total

    @api.depends(
        "fixed_expense_ids",
        "fixed_expense_ids.price_subtotal",
    )
    @api.multi
    def _compute_amount_total_fixed(self):
        for document in self:
            total = 0.0
            for line in document.fixed_expense_ids:
                total += line.price_subtotal
            document.amount_total_fixed = total

    @api.depends(
        "amount_total_transportation",
        "amount_total_daily",
        "amount_total_fixed",
    )
    @api.multi
    def _compute_amount_total(self):
        for document in self:
            document.amount_total = document.amount_total_transportation + \
                document.amount_total_daily + \
                document.amount_total_fixed

    @api.depends(
        "currency_id",
    )
    def _compute_allowed_pricelist_ids(self):
        obj_pricelist = self.env["product.pricelist"]
        for document in self:
            result = []
            if document.currency_id:
                criteria = [
                    ("currency_id", "=", document.currency_id.id),
                ]
                result = obj_pricelist.search(criteria).ids
            document.allowed_pricelist_ids = result

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
        comodel_name="hr.travel_request_type",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    allowed_realization_method_ids = fields.Many2many(
        string="Allowed Realization Methods",
        comodel_name="hr.travel_request_realization_method",
        related="type_id.allowed_realization_method_ids",
        store=False,
        readonly=True,
    )
    allowed_pricelist_ids = fields.Many2many(
        string="Allowed Pricelists",
        comodel_name="product.pricelist",
        compute="_compute_allowed_pricelist_ids",
        store=False,
    )
    pricelist_id = fields.Many2one(
        string="Pricelist",
        comodel_name="product.pricelist",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_depart = fields.Date(
        string="Date Depart",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_arrive = fields.Date(
        string="Date Depart",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    days_travel = fields.Integer(
        string="Day(s) Travel",
        compute="_compute_days_travel",
        store=True,
    )
    depart_from = fields.Char(
        string="Depart From",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    arrive_to = fields.Char(
        string="Arrive To",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    travel_purpose = fields.Text(
        string="Travel Purpose",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    transportation_expense_ids = fields.One2many(
        string="Transportation Expenses",
        comodel_name="hr.travel_request_transportation_expense",
        inverse_name="request_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    daily_expense_ids = fields.One2many(
        string="Daily Expenses",
        comodel_name="hr.travel_request_daily_expense",
        inverse_name="request_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    fixed_expense_ids = fields.One2many(
        string="Fixed Expenses",
        comodel_name="hr.travel_request_fixed_expense",
        inverse_name="request_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    amount_total_transportation = fields.Monetary(
        string="Total Transportation Expense",
        compute="_compute_amount_total_transportation",
        store=True,
    )
    amount_total_daily = fields.Monetary(
        string="Total Daily Expense",
        compute="_compute_amount_total_daily",
        store=True,
    )
    amount_total_fixed = fields.Monetary(
        string="Total Fixed Expense",
        compute="_compute_amount_total_fixed",
        store=True,
    )
    amount_total = fields.Monetary(
        string="Total Expense",
        compute="_compute_amount_total",
        store=True,
    )
    note = fields.Text(
        string="Note",
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("done", "Approved"),
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
            document._run_realization_method_confirm_method()

    @api.multi
    def action_approve(self):
        for document in self:
            document.write(document._prepare_approve_data())
            document._run_realization_method_approve_method()

    @api.multi
    def action_cancel(self):
        for document in self:
            document.write(document._prepare_cancel_data())
            document._run_realization_method_cancel_method()

    @api.multi
    def action_restart(self):
        for document in self:
            document.write(document._prepare_restart_data())
            document._run_realization_method_restart_method()

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
    def _run_realization_method_confirm_method(self):
        self.ensure_one()
        for method in self.allowed_realization_method_ids:
            method_to_call = getattr(self, method.confirm_method)
            method_to_call()

    @api.multi
    def _run_realization_method_approve_method(self):
        self.ensure_one()
        for method in self.allowed_realization_method_ids:
            method_to_call = getattr(self, method.approve_method)
            method_to_call()

    @api.multi
    def _run_realization_method_cancel_method(self):
        self.ensure_one()
        for method in self.allowed_realization_method_ids:
            method_to_call = getattr(self, method.cancel_method)
            method_to_call()

    @api.multi
    def _run_realization_method_restart_method(self):
        self.ensure_one()
        for method in self.allowed_realization_method_ids:
            method_to_call = getattr(self, method.restart_method)
            method_to_call()

    @api.multi
    def confirm_manual_procurement(self):
        self.ensure_one()
        pass

    @api.multi
    def approve_manual_procurement(self):
        self.ensure_one()
        pass

    @api.multi
    def cancel_manual_procurement(self):
        self.ensure_one()
        pass

    @api.multi
    def restart_manual_procurement(self):
        self.ensure_one()
        pass

    @api.multi
    def unlink(self):
        strWarning = _("You can only delete data on draft state")
        for document in self:
            if document.state != "draft":
                if not self.env.context.get("force_unlink", False):
                    raise UserError(strWarning)
        _super = super(HrTravelRequest, self)
        _super.unlink()

    @api.multi
    def validate_tier(self):
        _super = super(HrTravelRequest, self)
        _super.validate_tier()
        for document in self:
            if document.validated:
                document.action_approve()

    @api.onchange(
        "type_id",
        "pricelist_id",
    )
    def onchange_daily_expense_ids(self):
        self.update({"daily_expense_ids": [(5, 0, 0)]})

        if self.type_id and self.pricelist_id:
            result = []
            for line in self.type_id.daily_expense_ids:
                result.append((0, 0, {
                    "sequence": line.sequence,
                    "pricelist_id": self.pricelist_id.id,
                    "product_id": line.product_id.id,
                    "quantity": line.quantity,
                    "realization_method": line.realization_method_id.id,
                }))
            self.update({"daily_expense_ids": result})

            for line in self.daily_expense_ids:
                line.onchange_approve_quantity()
                line.onchange_price_unit()
                line.onchange_approve_price_unit()

    @api.onchange(
        "type_id",
        "pricelist_id",
    )
    def onchange_transportation_expense_ids(self):
        self.update({"transportation_expense_ids": [(5, 0, 0)]})

        if self.type_id and self.pricelist_id:
            result = []
            for line in self.type_id.transportation_expense_ids:
                result.append((0, 0, {
                    "sequence": line.sequence,
                    "pricelist_id": self.pricelist_id.id,
                    "product_id": line.product_id.id,
                    "quantity": line.quantity,
                    "round_trip": line.round_trip,
                    "realization_method": line.realization_method_id.id,
                }))
            self.update({"transportation_expense_ids": result})

            for line in self.transportation_expense_ids:
                line.onchange_approve_quantity()
                line.onchange_price_unit()
                line.onchange_approve_price_unit()

    @api.onchange(
        "type_id",
        "pricelist_id",
    )
    def onchange_fixed_expense_ids(self):
        self.update({"fixed_expense_ids": [(5, 0, 0)]})

        if self.type_id and self.pricelist_id:
            result = []
            for line in self.type_id.fixed_expense_ids:
                result.append((0, 0, {
                    "sequence": line.sequence,
                    "pricelist_id": self.pricelist_id.id,
                    "product_id": line.product_id.id,
                    "quantity": line.quantity,
                    "realization_method": line.realization_method_id.id,
                }))
            self.update({"fixed_expense_ids": result})

            for line in self.fixed_expense_ids:
                line.onchange_approve_quantity()
                line.onchange_price_unit()
                line.onchange_approve_price_unit()

    @api.onchange(
        "currency_id",
    )
    def onchange_pricelist_id(self):
        self.pricelist_id = False

    @api.multi
    def _check_realization_method(self, code):
        self.ensure_one()
        obj_method = self.env["hr.travel_request_realization_method"]
        criteria = [
            ("code", "=", code)
        ]
        methods = obj_method.search(criteria)
        if len(methods) > 0:
            method = methods[0]
        else:
            method = False

        result = False

        if method:
            daily_expenses = self.daily_expense_ids.filtered(
                lambda r: r.realization_method_id.id == method.id)
            if len(daily_expenses) > 0:
                result = True

        if method and not result:
            fixed_expenses = self.fixed_expense_ids.filtered(
                lambda r: r.realization_method_id.id == method.id)
            if len(fixed_expenses) > 0:
                result = True

        if method and not result:
            transportation_expenses = self.transportation_expense_ids.filtered(
                lambda r: r.realization_method_id.id == method.id)
            if len(transportation_expenses) > 0:
                result = True

        return result
