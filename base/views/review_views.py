from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from base.models import Item, Review, Favorite
from django.db.models import Count
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

@login_required
def delete_reviewed_item(request, item_id):
    # 自分のレビューだけ削除
    Review.objects.filter(user=request.user, item_id=item_id).delete()
    return redirect('my_review_list')



class MyReviewListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    自分が書いたレビューに紐づく『お店(Item)』だけを名前リンクで表示。
    ItemListView とクラス名が被らないように、別クラス名にしています。
    """
    model = Item
    template_name = 'pages/my_review_list.html'
    context_object_name = 'items'
    paginate_by = 20

    # 有料会員のみアクセス可
    def test_func(self):
        return getattr(self.request.user, 'is_premium', False)

    # 非会員は課金ページ等へ誘導（必要に応じて変更）
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('premium')  # URL名は環境に合わせて
        return super().handle_no_permission()

    def get_queryset(self):
        # 自分のレビューが1件でもある Item を重複なしで取得
        # 最新のレビュー日時順に近い形で並べたい場合は以下の order_by を使用
        return (
            Item.objects.filter(reviews__user=self.request.user)
                        .distinct()
                        .order_by('-reviews__created_at')
            # 必要に応じて .only('id', 'name') などで絞る
        )

@login_required
def favorite_items(request):
    user = request.user
    if not getattr(user, "is_premium", False):
        return redirect('premium')
    
    # ユーザーのお気に入りItemを取得
    favorites = Favorite.objects.filter(user=user).select_related('item')
    items = [f.item for f in favorites]

    return render(request, 'pages/favorite.html', {'items': items})

@login_required
def toggle_favorite(request, item_id):
    user = request.user
    if not getattr(user, "is_premium", False):
        return redirect('premium')

    item = Item.objects.get(id=item_id)
    fav, created = Favorite.objects.get_or_create(user=user, item=item)
    if not created:
        # すでにあれば削除
        fav.delete()
    return redirect('item_detail', pk=item.id)


def reviewed_items(request):
    # レビューが1件以上あるアイテムだけ取得
    items = Item.objects.annotate(review_count=Count("reviews")).filter(review_count__gt=0)
    return render(request, "snippets/review.html", {"reviewed_items": items})


@login_required
def review_write(request, item_id):
    # 投稿対象のお店を取得
    item = get_object_or_404(Item, id=item_id)

    # 有料会員チェック
    if not getattr(request.user, 'is_premium', False):
        return redirect("premium")

    if request.method == "POST":
        title = request.POST.get("title")
        rating = request.POST.get("rating")
        content = request.POST.get("content")

        # Review を作成
        Review.objects.create(
            user=request.user,
            item=item,
            title=title,
            rating=int(rating),
            content=content
        )

        # 投稿後は詳細ページにリダイレクト
        return redirect('item_detail', pk=item.id)

    # GET の場合は投稿フォームを表示
    return render(request, "pages/review_write.html", {"item": item})

def premium(request):
    # ログインしているユーザーを取得
    user = request.user
    # 有料会員に変更
    user.is_premium = True
    user.save()

    # 有料会員登録が完了したらトップページにリダイレクト
    return redirect('top')  # トップページのURL nameに変更して