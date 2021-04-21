{
    'name': 'hr_birthday_reminder',
    'summary': 'Birthday Reminder',
    'description': 'A module that sends birthday reminders to a list of employees',
    'author': 'Aleksandra Shumkoska',
    'category': 'Human Resources/Employees',
    'version': '0.1',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_birthday_reminder_templates.xml',
        'data/hr_birthday_reminder_cron.xml',
        'views/hr_birthday_reminder_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_department_views.xml'
    ]
}
