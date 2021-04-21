from odoo import models, fields, api


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    reminder_ids = fields.One2many('hr.birthday.reminder', 'department_id', string='Birthday Reminders',
                                   help='Birthday reminders for one or more groups of employees.')
