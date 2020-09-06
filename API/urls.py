from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('register/', views.registration_view, name='api-register'),
    path('login/', views.ObtainAuthTokenView.as_view(), name='api-login'),
    path('users/', views.UserList.as_view(), name='api-users'),
    path('user/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    path('parent-profile/<int:pk>/', views.ParentProfileView.as_view(), name='parentprofile-detail'),
    path('child-profile/<int:pk>/', views.ChildrenProfileView.as_view(), name='childrenprofile-detail'),
    path('register_child/', views.register_child_view, name='register-child'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('images/', views.ImageListView.as_view(), name='images'),
    path('videos/', views.VideoListView.as_view(), name='videos'),
    path('category/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('image/<int:pk>/', views.ImageView.as_view(), name='image-detail'),
    path('video/<int:pk>/', views.VideoView.as_view(), name='video-detail'),
    path('delete-child-profile/<int:pk>/', views.delete_child_view, name='delete'),
    path('documentation/', views.documentation, name='documentation'),
    path('password-reset/<uidb64>/<token>/', views.PasswordTokenCheckApi.as_view(), name='password-reset-confirm'),
    path('request-reset-email/', views.RequestPasswordResetEmail.as_view(), name='request-reset-email'),
    path('password-reset-complete/', views.SetNewPasswordAPIView.as_view(), name='password-reset-complete'),
]