from django.urls import path

from . import views


app_name = 'blog'

urlpatterns = [
    path(
        '',
        views.PostListView.as_view(),
        name='index'
    ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryList.as_view(),
        name='category_posts'
    ),
    path(
        'posts/<int:pk>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:pk>/edit/',
        views.EditPost.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:pk>/delete/',
        views.DeletePost.as_view(),
        name='delete_post'
    ),
    path(
        'profile/<str:username>/',
        views.ProfileListlView.as_view(),
        name='profile'
    ),
    path(
        'profile/user/edit/',
        views.ProfileUpdateView.as_view(),
        name='edit_profile'
    ),
    path(
        'posts/<int:pk>/<comment/',
        views.add_comment,
        name='add_comment'
    ),
    path(
        'posts/<int:post_pk>/edit_comment/<int:pk>/',
        views.CommentUpdate.as_view(), name='edit_comment'),
    path(
        'posts/<int:post_pk>/delete_comment/<int:pk>/',
        views.CommentDelete.as_view(),
        name='delete_comment'
    ),
]
