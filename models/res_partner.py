from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    reminder_ids = fields.Many2many('hr.birthday.reminder', 'reminder_partner_rel', 'partner_id', 'reminder_id',
                                    string='Birthday Reminders')
