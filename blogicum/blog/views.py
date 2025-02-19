from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .constants import MAX_COUNT_POST
from .forms import CommentForm, PostForm, UserForm
from .mixin import FilterMixin, OnlyAuthorMixin
from .models import Category, Comment, Post, User


class PostListView(FilterMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = MAX_COUNT_POST


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username
        })


class ProfileListlView(FilterMixin, ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = MAX_COUNT_POST

    def get_queryset(self):
        username = self.kwargs['username']
        self.profile = get_object_or_404(User, username=username)
        return super().get_queryset(
            self.request.user != self.profile
        ).filter(author=self.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username
        })


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if (
            not post.is_published
            or not post.category.is_published
            or post.pub_date > timezone.now()
        ) and post.author != self.request.user:
            raise Http404("Не доступно")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author').all()
        )
        return context


class EditPost(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'pk': self.object.pk
        })

    def handle_no_permission(self):
        post_id = self.kwargs.get('pk')
        return redirect(
            'blog:post_detail',
            pk=post_id
        )


class DeletePost(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username
        })


class CategoryList(FilterMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = MAX_COUNT_POST

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        queryset = super().get_queryset().filter(
            category=self.category
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', pk=pk)


class CommentUpdate(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'pk': self.object.post.pk
        })


class CommentDelete(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'pk': self.object.post.pk
        })
