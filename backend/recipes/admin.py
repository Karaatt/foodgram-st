from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Recipe, Ingredients, RecipeIngredient, Favorite, Subscription, ShoppingCart
from users.models import User


@admin.register(User)
class UserAdminPanel(UserAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email', 'is_staff')
    search_fields = ('email', 'username')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdminPanel(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_count')
    search_fields = ('name', 'author__username')
    list_filter = ('cooking_time',)
    inlines = [RecipeIngredientInline]

    def favorite_count(self, obj):
        return obj.favorited_by.count()
    favorite_count.short_description = 'В избранном'


@admin.register(Ingredients)
class IngredientAdminPanel(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Favorite)
class FavoriteAdminPanel(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(Subscription)
class SubscriptionAdminPanel(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')


@admin.register(ShoppingCart)
class ShoppingCartAdminPanel(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
