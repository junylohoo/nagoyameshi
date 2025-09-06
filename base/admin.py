# base/admin.py
from django.contrib import admin
from .models.item_models import Item, Category, Tag, Review, Favorite
from django import forms

# ---------------------------------------
# Category / Tag
# ---------------------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name')
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name')
    search_fields = ('name',)

# ---------------------------------------
# Item
# ---------------------------------------
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_published', 'created_at')
    list_filter = ('is_published', 'category', 'tags')
    search_fields = ('name', 'description')
    filter_horizontal = ('tags',)  # タグを複数選択可能
    readonly_fields = ('created_at', 'updated_at')  # 作成・更新日時は読み取り専用

# ---------------------------------------
# Review（評価は1〜5のプルダウン）
# ---------------------------------------
class ReviewAdminForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'
        widgets = {
            'rating': forms.Select(choices=Review.RATING_CHOICES)
        }

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    form = ReviewAdminForm
    list_display = ('user', 'item', 'rating', 'content', 'created_at')
    list_filter = ('rating',)
    search_fields = ('content',)
    readonly_fields = ('created_at',)

# ---------------------------------------
# Favorite
# ---------------------------------------
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'item')
    search_fields = ('user__username', 'item__name')
