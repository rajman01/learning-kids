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
                          RegisterChildSerializer, CategorySerializer, ImageSerializers, VideoSerializers,
                          ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer)
from rest_framework.authentication import TokenAuthentication
from users.models import ParentProfile, ChildrenProfile
from main.models import Category, Image, Video
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse as reset_reverse
from .utils import Util


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
        'images': reverse('images', request=request, format=format),
        'videos': reverse('videos', request=request, format=format),
        'request-reset-email': reverse('request-reset-email', request=request, format=format),
        'password-rest-complete': reverse('password-reset-complete', request=request, format=format)

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
            return Response({'error': 'All credentials must be provided'},status=status.HTTP_400_BAD_REQUEST)
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
            return Response({'response': 'you don\'t have permission to edit that'}, status=status.HTTP_403_FORBIDDEN)
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
            return Response({'response': 'you don\'t have permission to edit that'}, status=status.HTTP_403_FORBIDDEN)
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
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def put(self, request, *args, **kwargs):
        object = self.get_object()
        user = request.user
        if object.parent.user != user:
            return Response({'response': 'you don\'t have permission to edit that'}, status=status.HTTP_403_FORBIDDEN)
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
        return Response({'response': 'you don\'t have permission to delete that'}, status=status.HTTP_403_FORBIDDEN)
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
            return Response({'response': 'you don\'t have permission to do that'}, status=status.HTTP_403_FORBIDDEN)
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


class VideoListView(generics.ListAPIView):
    search_fields = ['name']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    queryset = Video.objects.all().order_by('-pk')
    serializer_class = VideoSerializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = PageNumberPagination


class ImageListView(generics.ListAPIView):
    search_fields = ['name']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    queryset = Image.objects.all().order_by('-pk')
    serializer_class = ImageSerializers
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


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            email = request.data['email']
        except KeyError:
            return Response({'error': 'Email must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reset_reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            absurl = 'https://' + current_site + relativeLink
            email_body = f'Hello {user.username}, \n use the link below to reset your password \n {absurl}'
            data = {'email_body': email_body, 'to_email': user.email, 'email_subject': 'Reset your password'}
            Util.send_email(data=data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckApi(generics.GenericAPIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token not valid please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({'success': True, 'message': 'Credentials Valid', 'uidb64': uidb64, 'token': token},
                            status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as identifier:
            if not PasswordResetTokenGenerator().check_token(user):
                return Response({'error': 'Token is not valid, please request a new one'},
                                status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = []
    authentication_classes = []

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)