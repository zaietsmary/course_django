from django.core.management.base import BaseCommand
from django.utils import timezone

from hr.models import Employee

class Command(BaseCommand):
    help = 'Set "is_active" as True for all Employees'

    def handle(self, *args, **kwargs):
        updated = Employee.objects.filter(is_active=False).update(is_active=True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated} employees.",
            ),
        )

