from datetime import datetime, date, timedelta

from odoo import fields
from odoo.tests.common import SavepointCase, tagged


@tagged('birthday_reminder')
class TestHrBirthdayReminder(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test department
        cls.department = cls.env['hr.department'].create({
            'name': "The Night's Watch"
        })
        # Create test users and employees
        cls.recepient_user = cls.env['res.users'].create({
            'name': 'Samwell Tarly',
            'login': 'sam@test.com'
        })
        cls.recepient_employee = cls.env['hr.employee'].create({
            'name': 'Samwell Tarly',
            'user_id': cls.recepient_user.id
        })
        cls.celebrant_user = cls.env['res.users'].create({
            'name': 'John Snow',
            'login': 'john@test.com'
        })
        cls.celebrant_employee = cls.env['hr.employee'].create({
            'name': 'John Snow',
            'birthday': date.today() + timedelta(days=10),
            'birthday_reminder': True,
            'user_id': cls.celebrant_user.id
        })
        # Create test birthday reminder
        cls.birthday_reminder = cls.env['hr.birthday.reminder'].create({
            'name': 'Test Birthday Reminder',
            'department_id': cls.department.id,
            'days_before_birthday': 5,
            'recepients_ids': [(6, 0, [cls.recepient_employee.user_partner_id.id,
                                       cls.celebrant_employee.user_partner_id.id])]
        })

    def test_compute_next_birthday_date(self):
        expected_next_birthday_date = date.today() + timedelta(days=10)
        self.assertEqual(self.celebrant_employee.next_birthday_date, expected_next_birthday_date,
                         'Next birthday date should be in 10 days.')

    def test_get_next_birthday_date(self):
        today = date.today()

        # If it's a past date, the next birthday should be next year
        birthday = date(1995, today.month, today.day - 1)
        expected_next_birthday = datetime(today.year + 1, birthday.month, birthday.day)
        actual_next_birthday = self.env['hr.employee']._get_next_birthday_date(birthday)
        self.assertEqual(actual_next_birthday, expected_next_birthday,
                         'Next birthday date should be next year.')

        # If it's a future date, the next birthday should be this year
        birthday = date(1995, today.month, today.day + 1)
        expected_next_birthday = datetime(today.year, birthday.month, birthday.day)
        actual_next_birthday = self.env['hr.employee']._get_next_birthday_date(birthday)
        self.assertEqual(actual_next_birthday, expected_next_birthday,
                         'Next birthday date should be this year.')

    def test_search_next_birthday_date(self):
        employee = self.env['hr.employee'].search([('next_birthday_date', '=', date.today() + timedelta(days=10))])
        self.assertTrue(employee, 'An employee with this next birthday date should exist.')

    def test_compute_birthday_remind_date(self):
        expected_birthday_remind_date = date.today() + timedelta(days=5)
        self.assertEqual(self.celebrant_employee.birthday_remind_date, expected_birthday_remind_date,
                         'Next birthday reminder date should be in 5 days.')

    def test_search_birthday_remind_date(self):
        remind_date = date.today()
        employee = self.env['hr.employee'].search([('birthday_remind_date', '>', remind_date)])
        self.assertTrue(employee, 'An employee with this birthday reminder date should exist.')
