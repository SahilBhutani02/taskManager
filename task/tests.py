from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Task

class TaskAPITestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass456')

        Task.objects.create(user=self.user1, title='Task 1', description='Desc 1', completed=False)
        Task.objects.create(user=self.user1, title='Task 2', description='Desc 2', completed=True)

        self.list_url = reverse('task-list-create')

    # Unauthenticated user can see all tasks
    def test_list_tasks_unauthenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    # Authenticated user sees only their tasks
    def test_list_tasks_authenticated(self):
        self.client.login(username='user1', password='pass123')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    # Filter by completed
    def test_filter_completed_true(self):
        self.client.login(username='user1', password='pass123')
        response = self.client.get(self.list_url, {'completed': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['completed'])

    def test_filter_completed_false(self):
        self.client.login(username='user1', password='pass123')
        response = self.client.get(self.list_url, {'completed': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertFalse(response.data['results'][0]['completed'])

    # Create task (authenticated)
    def test_create_task_authenticated(self):
        self.client.login(username='user1', password='pass123')
        data = {
            'title': 'New Task',
            'description': 'New Desc',
            'completed': False
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.filter(user=self.user1).count(), 3)

    # Create task (unauthenticated)
    def test_create_task_unauthenticated(self):
        data = {
            'title': 'New Task',
            'description': 'New Desc',
            'completed': False
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Retrieve a task detail
    def test_retrieve_task_detail(self):
        task = Task.objects.filter(user=self.user1).first()
        url = reverse('task-detail', kwargs={'pk': task.id})
        self.client.login(username='user1', password='pass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], task.id)

    # Update a task
    def test_update_task(self):
        task = Task.objects.filter(user=self.user1).first()
        url = reverse('task-detail', kwargs={'pk': task.id})
        self.client.login(username='user1', password='pass123')
        data = {
            'title': 'Updated Task',
            'description': task.description,
            'completed': True
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Task')
        self.assertTrue(task.completed)

    # Delete a task
    def test_delete_task(self):
        task = Task.objects.filter(user=self.user1).first()
        url = reverse('task-detail', kwargs={'pk': task.id})
        self.client.login(username='user1', password='pass123')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())
