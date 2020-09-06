from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import ParentProfile, ChildrenProfile
from main.models import Category, Image, Video
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import AuthenticationFailed


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']

    def save(self, **kwargs):
        try:
            email = self.validated_data['email']
            password1 = self.validated_data['password1']
            password2 = self.validated_data['password2']
        except KeyError:
            raise serializers.ValidationError({'error': 'All credentials must be provided'})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'email already exist'})
        account = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
        )
        if password1 != password2:
            raise serializers.ValidationError({'password': 'Password must match'})
        if len(password1) < 4:
            raise serializers.ValidationError({'password': 'Password too short'})
        account.set_password(password1)
        account.save()
        return account


class UserSerializer(serializers.HyperlinkedModelSerializer):
    parentprofile = serializers.HyperlinkedRelatedField(
        view_name='parentprofile-detail',
        read_only=True,
        many=False
    )

    class Meta:
        model = User
        fields = ['url', 'id', 'email', 'username', 'first_name', 'last_name', 'parentprofile', ]
        read_only_fields = ['id', ]


class ParentProfileSerializer(serializers.HyperlinkedModelSerializer):
    childrenprofile_set = serializers.HyperlinkedRelatedField(
        view_name='childrenprofile-detail',
        read_only=True,
        many=True
    )

    class Meta:
        model = ParentProfile
        fields = ['url', 'id', 'user', 'avatar', 'childrenprofile_set']


class ChildrenProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChildrenProfile
        fields = ['url', 'id', 'parent', 'name', 'age', 'gender', 'avatar', ]


class RegisterChildSerializer(serializers.ModelSerializer):
    parent_username = serializers.CharField()
    child_name = serializers.CharField()

    class Meta:
        model = ChildrenProfile
        fields = ['parent_username', 'child_name', 'age', 'gender']

    def save(self, **kwargs):
        try:
            parent_username = self.validated_data['parent_username']
            child_name = self.validated_data['child_name']
            age = self.validated_data['age']
            gender = self.validated_data['gender']
        except KeyError:
            raise serializers.ValidationError({'error': 'All credentials must be provided'})
        try:
            user = User.objects.get(username=parent_username)
        except User.DoesNotExist:
            raise serializers.ValidationError({'user': 'user does not exist'})
        child_profile = ChildrenProfile.objects.filter(parent=user.parentprofile, name=child_name).first()
        if child_profile:
            raise serializers.ValidationError({'profile': 'child name provided already exist for this parent'})
        else:
            child_profile = ChildrenProfile(
                parent=user.parentprofile,
                name=child_name,
                age=int(age),
                gender=gender
            )
            child_profile.save()
            return child_profile


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    image_set = serializers.HyperlinkedRelatedField(
        view_name='image-detail',
        read_only=True,
        many=True
    )
    video_set = serializers.HyperlinkedRelatedField(
        view_name='video-detail',
        read_only=True,
        many=True
    )

    class Meta:
        model = Category
        fields = ['url', 'id', 'name', 'description', 'image_set', 'video_set']


class ImageSerializers(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Image
        fields = ['url', 'id', 'category', 'name', 'image_description', 'image']


class VideoSerializers(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Video
        fields = ['url', 'id', 'category', 'name', 'video_description', 'video_link']


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)