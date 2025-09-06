# base/views/item_views.py
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Avg, Count
from base.models import Item, Category, Favorite

class ItemListView(ListView):
    model = Item
    template_name = 'pages/items.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=category_slug)
        return (
            Item.objects.filter(is_published=True, category__slug=category_slug)
                        .select_related('category')
                        .annotate(avg_rating=Avg('reviews__rating'),
                                  review_count=Count('reviews'))
                        .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['category'] = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return ctx

# お店の詳細ページ
# item_views.py


class ItemDetailView(DetailView):
    model = Item
    template_name = 'pages/item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # レビュー
        reviews = self.object.reviews.order_by('-created_at')
        ctx['reviews'] = reviews
        avg = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        ctx['avg_rating'] = round(avg, 1) if avg else None

        # お気に入り状態（ユーザーがログイン＆有料会員の場合のみ）
        user = self.request.user
        if user.is_authenticated and getattr(user, 'is_premium', False):
            ctx['is_favorite'] = Favorite.objects.filter(user=user, item=self.object).exists()
        else:
            ctx['is_favorite'] = False

        return ctx

