# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrTravelRequest(models.Model):
    _name = "hr.travel_request"
    _inherit = "hr.travel_request"

    @api.depends(
        "type_id",
    )
    def _can_cash_advance(self):
        for document in self:
            result = document._check_realization_method("CA")

        document.can_cash_advance = result

    advance_id = fields.Many2one(
        string="# Cash Advance",
        comodel_name="hr.advance",
        readonly=True,
        ondelete="restrict",
    )
    # Policy Field
    can_cash_advance = fields.Boolean(
        string="Can Create Cash Advance",
        compute="_can_cash_advance",
        store=False,
    )

    @api.multi
    def confirm_cash_advance(self):
        self.ensure_one()
        pass

    @api.multi
    def approve_cash_advance(self):
        self.ensure_one()
        if self.can_cash_advance:
            self._create_cash_advance()

    @api.multi
    def cancel_cash_advance(self):
        self.ensure_one()
        self._remove_cash_advance()

    @api.multi
    def restart_cash_advance(self):
        self.ensure_one()
        pass

    @api.multi
    def _remove_cash_advance(self):
        self.ensure_one()

        if self.advance_id:
            advance = self.advance_id
            self.write({"advance_id": False})
            advance.action_cancel()
            advance.action_restart()
            advance.unlink()

    @api.multi
    def _create_cash_advance(self):
        self.ensure_one()

        obj_advance = self.env["hr.advance"]
        advance_cache = obj_advance.new(self._prepare_cash_advance())
        advance_cache.onchange_journal_id()
        advance_cache.onchange_employee_advance_payable_account_id()
        advance_cache.onchange_employee_advance_account_id()
        advance_cache.onchange_input_type()
        advance = obj_advance.create(
            advance_cache._convert_to_write(advance_cache._cache))
        self.write({"advance_id": advance.id})
        advance.action_confirm()
        advance.action_approve()

    @api.multi
    def _prepare_cash_advance(self):
        self.ensure_one()
        line_ids = []
        obj_method = self.env["hr.travel_request_realization_method"]
        criteria = [
            ("code", "=", "CA")
        ]
        method = obj_method.search(criteria)[0]
        for daily_expense in self.daily_expense_ids.filtered(
                lambda r: r.realization_method_id.id == method.id):
            line_ids.append((0, 0, daily_expense._prepare_cash_advance_line()))

        for fixed_expense in self.fixed_expense_ids.filtered(
                lambda r: r.realization_method_id.id == method.id):
            line_ids.append((0, 0, fixed_expense._prepare_cash_advance_line()))

        for transportation_expense in self.transportation_expense_ids.filtered(
                lambda r: r.realization_method_id.id == method.id):
            line_ids.append(
                (0, 0, transportation_expense._prepare_cash_advance_line()))

        return {
            "name": self.name,
            "company_id": self.company_id.id,
            "project_id": self.project_id and self.project_id.id or False,
            "currency_id": self.currency_id.id,
            "employee_id": self.employee_id.id,
            "type_id": self.type_id.cash_advance_type_id.id,
            "date_request": fields.Date.today(),  # TODO
            "line_ids": line_ids,
        }
