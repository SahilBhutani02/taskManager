from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from .models import Task
from .serializers import RegisterSerializer, LoginSerializer, TaskSerializer


completed_param = openapi.Parameter(
    'completed', 
    openapi.IN_QUERY, 
    description="Filter tasks by completion status", 
    type=openapi.TYPE_BOOLEAN
)

@method_decorator(csrf_exempt, name='dispatch')
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.AllowAny] 
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['completed']

    @swagger_auto_schema(manual_parameters=[completed_param])
    def get(self, request):
        return super().get(request)


    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.filter(user=user)
        else:
            return Task.objects.all()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            raise PermissionDenied("You must be logged in to create a task.")


@method_decorator(csrf_exempt, name='dispatch')
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Task.objects.none() 
        
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.filter(user=user)
        return Task.objects.all()


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        login(request, user)
        return Response(
            {
                "message": "Login successful",
                "username": user.username
            },
            status=status.HTTP_200_OK
        )

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: openapi.Response('Logged out successfully')}
    )
    def post(self, request):
        logout(request)
        return Response(
            {"message": "Logged out successfully."},
            status=status.HTTP_200_OK
        )
