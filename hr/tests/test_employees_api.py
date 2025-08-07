from django.urls import reverse
from rest_framework import status
from rest_framework.test import (
    APIClient,
    APITestCase,
)

from hr.models import Employee, Position, Department
from hr.tests.factories import (
    EmployeeFactory,
    PositionFactory,
)


class EmployeeAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Employee.objects.create_user(username='testuser', password='testpassword', email='test@gmail.com')
        self.position = PositionFactory()
        self.client.force_authenticate(user=self.user)

    def test_get_employee_list(self):
        response = self.client.get(reverse('api-hr:employee-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_employee(self):
        data = {
            'username': 'newemployee',
            'first_name': 'Test',
            'last_name': 'Employee',
            'email': 'test@employee.com',
            'position': self.position.pk,
        }
        response = self.client.post(reverse('api-hr:employee-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_employee(self):
        employee = EmployeeFactory(position=self.position)
        data = {'first_name': 'Updated Name'}
        response = self.client.patch(reverse('api-hr:employee-detail', kwargs={'pk': employee.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_employee(self):
        employee = EmployeeFactory(position=self.position)
        response = self.client.delete(reverse('api-hr:employee-detail', kwargs={'pk': employee.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_search_employee(self):
        response = self.client.get(reverse('api-hr:employee-list'), {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class PositionViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Employee.objects.create_user(
            username='positionuser',
            password='testpassword',
            email='pos@test.com',
            is_staff=True,
            is_superuser=True
        )
        self.client.force_authenticate(user=self.user)
        self.position = PositionFactory()

    def test_get_position_list(self):
        response = self.client.get(reverse('api-hr:position-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)

    def test_retrieve_position(self):
        response = self.client.get(
            reverse('api-hr:position-detail', kwargs={'pk': self.position.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.position.pk)

    def test_create_position(self):
        department = Department.objects.create(name='Engineering')
        data = {
            'title': 'Developer',
            'department': department.id,
            'is_manager': False,
            'is_active': True,
            'job_description': 'Writing code',
            'monthly_rate': 10000
        }
        response = self.client.post(reverse('api-hr:position-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Developer')

    def test_update_position(self):
        data = {'title': 'Updated Title'}
        response = self.client.patch(
            reverse('api-hr:position-detail', kwargs={'pk': self.position.pk}),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_delete_position(self):
        response = self.client.delete(
            reverse('api-hr:position-detail', kwargs={'pk': self.position.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Position.objects.filter(pk=self.position.pk).exists())