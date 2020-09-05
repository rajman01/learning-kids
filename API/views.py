from django.shortcuts import render
from rest_framework import status, generics, filters
from rest_framework.reverse import reverse
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import (RegisterSerializer, UserSerializer, ParentProfileSerializer, ChildrenProfileSerializer,
                          RegisterChildSerializer, CategorySerializer, ImageSerializers, VideoSerializers)
from rest_framework.authentication import TokenAuthentication
from users.models import ParentProfile, ChildrenProfile
from main.models import Category, Image, Video
from rest_framework.pagination import PageNumberPagination


@api_view(['GET'])
@permission_classes(())
def api_root(request, format=None):
    return Response({
        'documentation': reverse('documentation', request=request, format=format),
        'users': reverse('api-users', request=request, format=format),
        'login': reverse('api-login', request=request, format=format),
        'register': reverse('api-register', request=request, format=format),
        'register-child': reverse('register-child', request=request, format=format),
        'categories': reverse('categories', request=request, format=format),

    })

@api_view(['GET'])
@permission_classes(())
def documentation(request):
    return render(request, 'API/documentation.html')


@api_view(['POST', ])
@permission_classes(())
def registration_view(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['response'] = 'successfully registered a Parent account'
            data['email'] = account.email
            data['username'] = account.username
            token = Token.objects.create(user=account)
            data['token'] = token.key
        else:
            data = serializer.errors
        return Response(data)


class ObtainAuthTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {}
        try:
            username = request.data['username']
            password = request.data['password']
        except KeyError:
            return Response({'error': 'All credentials must be provided'})
        user = authenticate(username=username, password=password)
        if user:
            try:
                token = Token.objects.get(user=user)
            except Token.DoesNotExist:
                token = Token.objects.create(user=user)
            context['response'] = 'Successfully authenticated.'
            context['pk'] = user.pk
            context['username'] = username
            context['token'] = token.key
        else:
            context['response'] = 'Error'
            context['error_message'] = 'Invalid credentials'
        return Response(context)


class UserList(generics.ListAPIView):
    queryset = User.objects.all().order_by('-pk')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = PageNumberPagination


class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def put(self, request, *args, **kwargs):
        object = self.get_object()
        user = request.user
        if object != user:
            return Response({'response': 'you don\'t have permission to edit that'})
        serializer = UserSerializer(object, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['success'] = 'update successful'
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ParentProfileView(generics.RetrieveUpdateAPIView):
    queryset = ParentProfile.objects.all()
    serializer_class = ParentProfileSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def put(self, request, *args, **kwargs):
        object = self.get_object()
        user = request.user
        if object.user != user:
            return Response({'response': 'you don\'t have permission to edit that'})
        serializer = ParentProfileSerializer(object, data=request.data, context={'request': request})
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['success'] = 'update successful'
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChildrenProfileView(generics.RetrieveUpdateAPIView):
    queryset = ChildrenProfile.objects.all()
    serializer_class = ChildrenProfileSerializer
    permission_classes = []
    authentication_classes = []

    def put(self, request, *args, **kwargs):
        object = self.get_object()
        user = request.user
        if object.parent.user != user:
            return Response({'response': 'you don\'t have permission to edit that'})
        serializer = ChildrenProfileSerializer(object, data=request.data, context={'request': request})
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['success'] = 'update successful'
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
@permission_classes((IsAuthenticated,))
def delete_child_view(request, pk):
    try:
        profile = ChildrenProfile.objects.get(pk=pk)
    except ChildrenProfile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    user = request.user
    if profile.parent.user != user:
        return Response({'response': 'you don\'t have permission to delete that'})
    if request.method == 'DELETE':
        operation = profile.delete()
        data = {}
        if operation:
            data['success'] = 'delete successful'
        else:
            data['failure'] = 'delete failed'
        return Response(data=data)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
@authentication_classes((TokenAuthentication,))
def register_child_view(request):
    if request.method == 'POST':
        user1 = request.user
        try:
            username = request.data['parent_username']
        except KeyError:
            return Response({'error': 'All credentials must be provided'})
        try:
            user2 = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'response': 'user does not exist'})
        if user1 != user2:
            return Response({'response': 'you don\'t have permission to do that'})
        serializer = RegisterChildSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            profile = serializer.save()
            data['response'] = 'successfully created'
            data['name'] = profile.name
            data['age'] = profile.age
            data['gender'] = profile.gender
        else:
            data = serializer.errors
        return Response(data)


class CategoryListView(generics.ListAPIView):
    search_fields = ['name']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    queryset = Category.objects.all().order_by('-pk')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = PageNumberPagination


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class ImageView(generics.RetrieveAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class VideoView(generics.RetrieveAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]