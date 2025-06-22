from django.http import HttpResponse
from django.db.models import Q
from hr.models import Department, Position


def homework_querysets(request):
    departments_with_managers = Department.objects.filter(position__is_manager=True).order_by('name')

    count_positions = Position.objects.filter(is_active=True).count()

    active_or_hr = Position.objects.filter(Q(is_active=True) | Q(department__name='HR'))

    department_names = Department.objects.filter(position__is_manager=True).values('name').distinct()

    positions = Position.objects.order_by('title').values('title', 'is_active')

    result = "=== Запит 1 ===\n" + "\n".join([d.name for d in departments_with_managers]) + "\n\n"
    result += f"=== Запит 2 ===\nКількість активних позицій: {count_positions}\n\n"
    result += "=== Запит 3 ===\n" + "\n".join([p.title for p in active_or_hr]) + "\n\n"
    result += "=== Запит 4 ===\n" + "\n".join([d['name'] for d in department_names]) + "\n\n"
    result += "=== Запит 5 ===\n"
    for p in positions:
        result += f"{p['title']} - Активна: {'Так' if p['is_active'] else 'Ні'}\n"

    return HttpResponse(result, content_type="text/plain; charset=utf-8")

