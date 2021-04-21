from odoo import models, fields, api


class HrBirthdayReminder(models.Model):
    _name = 'hr.birthday.reminder'
    _description = 'Birthday Reminder'
    _inherit = ['mail.thread']

    name = fields.Char(string='Birthday Reminder', required=True, help='Title of the birthday reminder.')
    days_before_birthday = fields.Integer(string='Days before Birthday', default=3, required=True,
                                          help='Number of days before the actual birthday.')
    recepients_ids = fields.Many2many('res.partner', 'reminder_partner_rel', 'reminder_id', 'partner_id',
                                      string='List of Recepients',
                                      help='The list of people who will receive the reminder notification.')
    department_id = fields.Many2one('hr.department', string='Department')
