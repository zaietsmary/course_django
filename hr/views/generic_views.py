import datetime

from django.core.cache import cache
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)

from hr.calculate_salary import CalculateMonthRateSalary
from hr.forms import (
    EmployeeForm,
    SalaryForm,
)
from hr.mixins import UserIsAdminMixin
from hr.models import Employee


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employee_list.html'
    context_object_name = 'employees'

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(position__title__icontains=search)
                | Q(email__icontains=search),
            )
        return queryset


class EmployeeCreateView(UserIsAdminMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_form.html'
    success_url = reverse_lazy('hr:employee_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Працівника успішно створено.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Виникла помилка при створенні працівника.')
        return super().form_invalid(form)


class EmployeeUpdateView(UserIsAdminMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_form.html'
    success_url = reverse_lazy('hr:employee_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Успішно оновлено!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Неможливо оновити!')
        return super().form_invalid(form)

class EmployeeDeleteView(UserIsAdminMixin, DeleteView):
    model = Employee
    template_name = 'employee_confirm_delete.html'
    success_url = reverse_lazy('hr:employee_list')


class EmployeeProfileView(UserIsAdminMixin, DetailView):
    model = Employee
    template_name = 'employee_profile.html'

    def get_object(self):
        employee_id = self.kwargs.get('pk')
        employee = cache.get(f'employee_{employee_id}')

        if not employee:
            employee = get_object_or_404(Employee, pk=employee_id)
            cache.set(f'employee_{employee_id}', employee, timeout=5 * 60)

        return employee


class SalaryCalculatorView(UserIsAdminMixin, FormView):
    template_name = 'salary_calculator.html'
    form_class = SalaryForm

    def get(self, request, *args, **kwargs):
        form = SalaryForm()
        return render(request, self.template_name, {'form': form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        employee = cleaned_data.get('employee')

        calculator = CalculateMonthRateSalary(employee=employee)

        days = {day: day_type for day, day_type in cleaned_data.items() if day.startswith(calculator.day_prefix)}

        salary = calculator.calculate_salary(days_dict=days)

        calculator.save_salary(salary=salary, date=datetime.date.today())

        return render(
            request=self.request,
            template_name=self.template_name,
            context={
                'form': form,
                'calculated_salary': salary,
            },
        )
