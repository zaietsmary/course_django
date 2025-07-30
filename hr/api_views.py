from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from hr.calculate_salary import CalculateMonthRateSalary
from hr.models import (
    Employee,
    Position, Department,
)
from hr.pydantic_models import WorkingDays
from hr.serializers import (
    EmployeeSerializer,
    PositionSerializer,
    SalarySerializer, DepartmentSerializer,
)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    @action(detail=True, methods=['get'])
    def employee_count(self, request, pk=None):
        department = self.get_object()
        count = Employee.objects.filter(position__department=department).count()
        return Response({'employee_count': count})


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(position__title__icontains=search) |
                Q(email__icontains=search),
            )
        return queryset

    @action(detail=True, methods=['get'])
    def position_count(self, request, pk=None):
        employee = self.get_object()
        count = Employee.objects.filter(position=employee.position).count()
        return Response({'position_count': count})


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class SalaryCalculatorView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SalarySerializer(data=request.data)
        if serializer.is_valid():

            calculator = CalculateMonthRateSalary(employee=serializer.validated_data['employee'])
            month_days = WorkingDays(
                working=serializer.validated_data['working_days'],
                sick=serializer.validated_data['sick_days'],
                holiday=serializer.validated_data['holiday_days'],
                vacation=serializer.validated_data['holiday_days'],
            )

            salary = calculator.calculate_salary(month_days=month_days)
            return Response({'salary': salary})

        return Response(serializer.errors, status=400)
