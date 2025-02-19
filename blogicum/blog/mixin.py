from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.utils import timezone

from .models import Post


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class FilterMixin:
    def get_queryset(self, post_published=True):
        queryset = Post.objects.select_related(
            'category', 'location', 'author'
        )
        if post_published:
            queryset = queryset.filter(
                pub_date__lt=timezone.now(),
                is_published=True,
                category__is_published=True
            )

        return queryset.order_by(
            '-pub_date'
        ).annotate(
            comment_count=Count('comments')
        )
