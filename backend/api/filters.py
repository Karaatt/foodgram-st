from recipes.models import Favorite, ShoppingCart


def apply_recipe_filters(queryset, request):
    user = request.user
    author_id = request.query_params.get('author')
    if author_id:
        queryset = queryset.filter(author_id=author_id)

    is_favorited = request.query_params.get('is_favorited')
    if is_favorited == '1':
        if user.is_authenticated:
            favorite_recipe_ids = Favorite.objects.filter(
                user=user
            ).values_list('recipe_id', flat=True)
            queryset = queryset.filter(id__in=favorite_recipe_ids)
        else:
            return queryset.none()

    is_in_cart = request.query_params.get('is_in_shopping_cart')
    if is_in_cart == '1':
        if user.is_authenticated:
            cart_recipe_ids = ShoppingCart.objects.filter(
                user=user
            ).values_list('recipe_id', flat=True)
            queryset = queryset.filter(id__in=cart_recipe_ids)
        else:
            return queryset.none()

    return queryset
