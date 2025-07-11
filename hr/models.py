from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

# from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Company name'))
    address = models.CharField(max_length=200, verbose_name=_('Company address'))
    email = models.EmailField(verbose_name=_('Company email'))
    tax_code = models.CharField(max_length=200, verbose_name=_('Company tax code'))

    def __str(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk and Company.objects.exists():
            raise ValidationError('There can be only one Company instance')
        return super(Company, self).save(*args, **kwargs)


class Department(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Department name'))
    parent_department = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Parent department'),
    )

    def __str__(self):
        return self.name


class Position(models.Model):
    title = models.CharField(max_length=100, verbose_name=_('Title'))
    department = models.ForeignKey('Department', on_delete=models.CASCADE, verbose_name=_('Department'))
    is_manager = models.BooleanField(default=False, verbose_name=_('Is manager'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    job_description = models.TextField(verbose_name=_('Job Description'))
    monthly_rate = models.IntegerField(default=0, verbose_name=_('Monthly rate'))

    def save(self, *args, **kwargs):
        if self.is_manager:
            existing_manager = (
                Position.objects.filter(
                    department=self.department,
                    is_manager=True,
                )
                .exclude(id=self.id)
                .exists()
            )
            if existing_manager:
                raise ValidationError(
                    f'Manager already exists in the {self.department.name} department.',
                )
        super(Position, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Employee(AbstractUser):
    hire_date = models.DateField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    position = models.ForeignKey(
        'Position', on_delete=models.SET_NULL, null=True, blank=True,
    )
    phone_number = models.CharField(max_length=151, default='')

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.position or ""}'


class MonthlySalary(models.Model):
    month_year = models.DateField()
    salary = models.IntegerField()
    bonus = models.IntegerField(null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    paid_date = models.DateField()
