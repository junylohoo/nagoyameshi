from django.contrib import admin
from django.urls import path
from base.views import accounts_views, item_views, review_views, reservation_views

urlpatterns = [
    # review_views.py にビューを作成
    path('my-reviews/', review_views.MyReviewListView.as_view(), name='my_review_list'),
    path('reservation/list/', reservation_views.reservation_list, name='reservation_list'),
    path('reservation/<str:item_id>/', reservation_views.make_reservation, name='make_reservation'),
    path('favorites/', review_views.favorite_items, name='favorite_items'),

    path('item/<str:item_id>/favorite/', review_views.toggle_favorite, name='toggle_favorite'),
    path('item/<str:pk>/', item_views.ItemDetailView.as_view(), name='item_detail'),


    path('reviews/', review_views.reviewed_items, name='reviewed_items'),
    
    path('webhook/stripe/', accounts_views.stripe_webhook, name='stripe_webhook'),

    path("review/write/<str:item_id>/", review_views.review_write, name="review_write"),


    path('items/<slug:category_slug>/', item_views.ItemListView.as_view(), name='item_list'),

    # お店の詳細ページ
    path('admin/', admin.site.urls),
    path('accounts/login/', accounts_views.login_view, name='login'),
    path('accounts/logout/',accounts_views.logout_view,name='logout'),
    path('accounts/signup/', accounts_views.signup_view, name='signup'),
    path('accounts/premium/', accounts_views.premium_view, name='premium'),
    path('accounts/premium/success/', accounts_views.premium_success, name='premium_success'),
    path('accounts/premium/cancel/', accounts_views.premium_cancel, name='premium_cancel'),
    path('', accounts_views.top_view, name='top'),

]