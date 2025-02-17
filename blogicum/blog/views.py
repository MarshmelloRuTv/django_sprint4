from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import (
    CreateView, ListView, DeleteView, UpdateView, DetailView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.utils.decorators import method_decorator

from .models import Post, Category, User, Congratulation
from .forms import PostForm, UserForm, CongratulationForm


MAX_COUNT_POST = 10


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class FilterMixin():
    def get_queryset(self):
        return Post.objects.filter(
            pub_date__lt=timezone.now(),
            is_published=True,
            category__is_published=True
        ).order_by(
            '-pub_date'
        ).annotate(
            comment_count=Count('congratulations')
        )


class PostListView(FilterMixin, LoginRequiredMixin, ListView):
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
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username
        })


class ProfileDetaillView(DetailView):
    model = User
    context_object_name = 'profile'
    template_name = 'blog/profile.html'
    paginate_by = MAX_COUNT_POST
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        if self.request.user != user:
            posts = Post.objects.filter(
                author=user,
                is_published=True,
                pub_date__lt=timezone.now()
            ).order_by(
                '-pub_date'
            ).annotate(
                comment_count=Count('congratulations')
            )
        else:
            posts = Post.objects.filter(
                author=user,
            ).order_by(
                '-pub_date'
            ).annotate(
                comment_count=Count('congratulations')
            )  # как можно сократить?

        paginator = Paginator(posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username
        })


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if (
            not post.is_published
            or not post.category.is_published
            or post.pub_date > timezone.now()
        ):
            if post.author != self.request.user:
                raise Http404("Не доступно")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CongratulationForm()
        context['comments'] = (
            self.object.congratulations.all()
        )
        return context


class EditPost(OnlyAuthorMixin, LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            'pk': self.object.pk
        })

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def handle_no_permission(self):
        post_id = self.kwargs.get('pk')
        return redirect(reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': post_id}
        ))
# можно как то без его, когда убираю тесты не проходят?


class DeletePost(OnlyAuthorMixin, LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Post, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username
        })


class CategoryList(FilterMixin, LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = MAX_COUNT_POST

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug']
        )
        if not self.category.is_published:
            raise Http404("Эта категория не опубликована.")
        queryset = super().get_queryset().filter(category=self.category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)

    form = CongratulationForm(request.POST)
    if form.is_valid():
        congratulation = form.save(commit=False)
        congratulation.author = request.user
        congratulation.post = post
        congratulation.save()

    return redirect('blog:post_detail', pk=pk)


class CommentUpdate(OnlyAuthorMixin, LoginRequiredMixin, UpdateView):
    model = Congratulation
    form_class = CongratulationForm
    template_name = 'blog/comment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.get_object()
        return context

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            'pk': self.object.post.pk
        })


class CommentDelete(OnlyAuthorMixin, LoginRequiredMixin, DeleteView):
    model = Congratulation
    template_name = 'blog/comment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.get_object()
        return context

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            'pk': self.object.post.pk
        })
