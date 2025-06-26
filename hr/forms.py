import calendar
from datetime import date

from django import forms
from django.forms import ChoiceField

from common.enums import WorkDayEnum
from hr.models import Employee


WorkDayChoices = [(tag.name, tag.value) for tag in WorkDayEnum]


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('username', 'first_name', 'last_name', 'email', 'position')


class SalaryForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        super(SalaryForm, self).__init__(*args, **kwargs)

        today = date.today()
        _, num_days = calendar.monthrange(today.year, today.month)

        for day in range(1, num_days + 1):
            weekday_name = calendar.day_name[calendar.weekday(today.year, today.month, day)]
            field_name = f'day_{day}'

            if calendar.weekday(today.year, today.month, day) >= 5:  # Saturday and Sunday
                self.fields[field_name] = ChoiceField(
                    label=f'{day} - {weekday_name}',
                    choices=[(WorkDayEnum.WEEKEND.name, WorkDayEnum.WEEKEND.value)],
                    initial=WorkDayEnum.WEEKEND.name,
                )
            else:
                self.fields[field_name] = ChoiceField(
                    label=f'{day} - {weekday_name}',
                    choices=WorkDayChoices,
                    initial=WorkDayEnum.WORKING_DAY.name,
                )
    def clean_employee(self):
        employee = self.cleaned_data.get('employee')
        if not employee:
            raise forms.ValidationError('Поле Employee: Переконайтеся, що поле employee заповнено.')
        return employee

    def clean(self):
        cleaned_data = super().clean()
        sick_count = 0
        holiday_count = 0

        for name, value in cleaned_data.items():
            if name.startswith('day_'):
                if value == WorkDayEnum.SICK_DAY.name:
                    sick_count += 1
                elif value == WorkDayEnum.HOLIDAY.name:
                    holiday_count += 1

        if sick_count > 5:
            raise forms.ValidationError(
                f'Кількість лікарняних днів не може перевищувати 5. Ви вибрали {sick_count}.'
            )

        if holiday_count > 3:
            raise forms.ValidationError(
                f'Кількість святкових днів не може перевищувати 3. Ви вибрали {holiday_count}.'
            )

        return cleaned_data
