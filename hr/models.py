from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
import datetime


class Company(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    email = models.EmailField()
    tax_code = models.CharField(max_length=200)

    def __str(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk and Company.objects.exists():
            raise ValidationError("There can be only one Company instance")
        return super(Company, self).save(*args, **kwargs)


class Department(models.Model):
    name = models.CharField(max_length=200)
    parent_department = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.name


class Position(models.Model):
    title = models.CharField(max_length=200)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    is_manager = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    job_description = models.CharField(max_length=500, default="")
    monthly_rate = models.IntegerField(default=0)

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
                    f"Manager already exists in the {self.department.name} department."
                )
        super(Position, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Employee(AbstractUser):
    hire_date = models.DateField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    position = models.ForeignKey(
        "Position", on_delete=models.SET_NULL, null=True, blank=True
    )
    phone_number = models.CharField(max_length=151, default="")

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.position or ""}'


class MonthlySalary(models.Model):
    month_year = models.DateField()
    salary = models.IntegerField()
    bonus = models.IntegerField(null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    paid_date = models.DateField(default=datetime.date.today)
