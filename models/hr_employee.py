from datetime import datetime, timedelta

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    birthday_reminder = fields.Boolean(string='Include in Birthday List',
                                       help='Include the birthday of this employee in the birthday reminders list.')
    next_birthday_date = fields.Date(string='Next Birthday', compute='_compute_next_birthday_date',
                                     search='_search_next_birthday_date', help='Date of the next birthday')
    birthday_remind_date = fields.Date(string='Birthday Remind Date', compute='_compute_birthday_remind_date',
                                       search='_search_birthday_remind_date', help='Date of the next birthday reminder')

    @api.depends('birthday')
    def _compute_next_birthday_date(self):
        """
        Computes the next birthday date based on the date of birth.
        """
        for record in self:
            if record.birthday:
                record.next_birthday_date = self._get_next_birthday_date(record.birthday)
            else:
                record.next_birthday_date = None

    @staticmethod
    def _get_next_birthday_date(birthday):
        """
        Calculates the next birthday date based on the date of birth.
        """
        now = datetime.now()
        current_year_bd = datetime(now.year, birthday.month, birthday.day)
        next_year_bd = datetime(now.year + 1, birthday.month, birthday.day)
        return current_year_bd if current_year_bd > now else next_year_bd

    @api.model
    def _search_next_birthday_date(self, operator, value):
        """
        Enables adding filters in the search view for the computed field next_birthday_date.
        :param operator: the search operator
        :param value: the search value
        """
        if operator not in ['=', '>', '>=', '<', '<=', '!=']:
            raise ValueError(_('This operator is not supported'))
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d').date()
        employees = self.search([('birthday_reminder', '=', True)])
        employee_ids = []
        for employee in employees:
            if employee.next_birthday_date and ((operator == '=' and employee.next_birthday_date == value) or
                                                (operator == '>' and employee.next_birthday_date > value) or
                                                (operator == '>=' and employee.next_birthday_date >= value) or
                                                (operator == '<' and employee.next_birthday_date < value) or
                                                (operator == '<=' and employee.next_birthday_date <= value) or
                                                (operator == '!=' and employee.next_birthday_date != value)):
                employee_ids.append(employee.id)
        return [('id', 'in', employee_ids)]

    @api.depends('next_birthday_date', 'user_partner_id', 'user_partner_id.reminder_ids',
                 'user_partner_id.reminder_ids.days_before_birthday')
    def _compute_birthday_remind_date(self):
        """
        Computes the date of the next birthday reminder based on the next birthday date and the reminder configuration.
        """
        for record in self:
            if record.user_partner_id and record.user_partner_id.reminder_ids:
                next_reminder = self._get_next_reminder(record)
                record.birthday_remind_date = record.next_birthday_date - timedelta(
                    days=next_reminder.days_before_birthday)
            else:
                record.birthday_remind_date = None

    @staticmethod
    def _get_next_reminder(employee):
        """
        Gets the next reminder list that the employee is a member of. One employee can be part of multiple different
        lists, so this method will use the one which is the earliest (and that is the one which has the maximum days
        before the birthday).
        :param employee: the employee we are getting the reminder for
        """
        return max(employee.user_partner_id.reminder_ids, key=lambda r: r.days_before_birthday)

    @api.model
    def _search_birthday_remind_date(self, operator, value):
        """
        Enables adding filters in the search view for the computed field birthday_remind_date.
        :param operator: the search operator
        :param value: the search value
        """
        if operator not in ['=', '>', '>=', '<', '<=', '!=']:
            raise ValueError(_('This operator is not supported'))
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d').date()
        employees = self.search([('birthday_reminder', '=', True)])
        employee_ids = []
        for employee in employees:
            if employee.birthday_remind_date and ((operator == '=' and employee.birthday_remind_date == value) or
                                                  (operator == '>' and employee.birthday_remind_date > value) or
                                                  (operator == '>=' and employee.birthday_remind_date >= value) or
                                                  (operator == '<' and employee.birthday_remind_date < value) or
                                                  (operator == '<=' and employee.birthday_remind_date <= value) or
                                                  (operator == '!=' and employee.birthday_remind_date != value)):
                employee_ids.append(employee.id)
        return [('id', 'in', employee_ids)]

    @api.model
    def send_birthday_reminder(self):
        """
        Sends a reminder email to all partners which are members of the reminder's list.
        """
        employees = self.search(['&', ('birthday_reminder', '=', True),
                                 ('birthday_remind_date', '=', fields.Date.today())])
        reminder_template = self.env.ref('hr_birthday_reminder.hr_birthday_reminder_email')

        for employee in employees:
            reminders = self.env['hr.birthday.reminder'].search(
                [('id', 'in', employee.user_partner_id.reminder_ids.ids)])
            recepients = reminders.mapped('recepients_ids')
            # Avoid sending an email to the employee which the reminder is for
            recepients -= employee.user_partner_id
            render_context = {
                'employee': employee
            }
            rendered_body = reminder_template._render(render_context, engine='ir.qweb')
            body = self.env['mail.render.mixin']._replace_local_links(rendered_body)
            mail = self.env['mail.mail'].sudo().create({
                'subject': _('Birthday Reminder for %s', employee.name),
                'email_from': self.env.user.email_formatted,
                'author_id': self.env.user.partner_id.id,
                'recipient_ids': [(4, pid) for pid in recepients.ids],
                'body_html': body,
            })
            mail.send()
