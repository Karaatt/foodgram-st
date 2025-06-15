from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    recipe_list,
    recipe_detail,
    ingredient_list,
    ingredient_detail,
    add_to_favorites,
    manage_shopping_cart,
    download_cart,
    get_short_link,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("recipes/", recipe_list, name="recipe-list"),
    path(
        "recipes/<int:id>/shopping_cart/",
        manage_shopping_cart,
        name="shopping-cart",
    ),
    path(
        "recipes/download_shopping_cart/", download_cart, name="download-cart"
    ),
    path("recipes/<int:id>/", recipe_detail, name="recipe-detail"),
    path("recipes/<int:id>/favorite/", add_to_favorites, name="favorite"),
    path("recipes/<int:id>/get-link/", get_short_link, name="short-link"),
    path("ingredients/", ingredient_list, name="ingredient-list"),
    path("ingredients/<int:id>/", ingredient_detail, 
         name="ingredient-detail"),
]
