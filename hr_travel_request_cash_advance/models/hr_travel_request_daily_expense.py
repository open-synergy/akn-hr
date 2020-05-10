# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class HrTravelRequestDailyExpense(models.Model):
    _name = "hr.travel_request_daily_expense"
    _inherit = "hr.travel_request_daily_expense"

    @api.multi
    def _prepare_cash_advance_line(self):
        self.ensure_one()
        return {
            "sequence": self.sequence,
            "product_id": self.product_id.id,
            "price_unit": self.price_unit,
            "quantity": self.quantity,
            "approve_price_unit": self.approve_price_unit,
            "approve_quantity": self.approve_quantity,
            "uom_id": self.uom_id.id,
        }
