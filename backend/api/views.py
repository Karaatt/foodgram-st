from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import (AllowAny, IsAuthenticated, 
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from djoser.views import UserViewSet
from recipes.models import (Recipe, Ingredients, Favorite, 
                            Subscription, ShoppingCart)
from users.models import User
from .serializers import (
    IngredientSerializer, RecipeReadSerializer, UserProfileSerializer,
    SubscriptionSerializer, RecipeWriteSerializer, AvatarUpdateSerializer,
    RecipeMiniSerializer, SubscribeCreateSerializer
)
from .pagination import CustomPagePagination
from .filters import apply_recipe_filters


class UserViewSet(UserViewSet):
    queryset = User.objects.all().order_by('id')
    pagination_class = CustomPagePagination

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = UserProfileSerializer(page or queryset, many=True,
                                           context={'request': request})
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs.get('id'))
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'], 
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserProfileSerializer(request.user, 
                                           context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe',
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        user = request.user
        if request.method == 'POST':
            serializer = SubscribeCreateSerializer(
                data=request.data, context={'request': request, 
                                            'author': author}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(author, 
                                                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = user.subscriptions.filter(author=author).first()
        if not subscription:
            return Response({'error': 'Подписка не найдена'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar',
            permission_classes=[IsAuthenticated])
    def avatar_update(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarUpdateSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        user.avatar.delete()
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='subscriptions',
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        authors = [sub.author for sub in request.user.subscriptions.all()]
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(page, many=True, 
                                            context={'request': request})
        if page:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def recipe_list(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = RecipeWriteSerializer(data=request.data, 
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        return Response(RecipeWriteSerializer(recipe, 
                        context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

    recipes = Recipe.objects.all().order_by('-id')
    recipes = apply_recipe_filters(recipes, request)
    paginator = CustomPagePagination()
    page = paginator.paginate_queryset(recipes, request)
    serializer = RecipeReadSerializer(page, many=True, 
                                      context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == 'PATCH':
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.user != recipe.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = RecipeWriteSerializer(recipe, data=request.data, 
                                           partial=True,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    if request.method == 'DELETE':
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.user != recipe.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = RecipeReadSerializer(recipe, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def get_short_link(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    short_url = reverse('short-link', args=[recipe.id])
    absolute_url = request.build_absolute_uri(short_url)
    full_url = absolute_url.replace('api/', '').replace('get-link/', '')
    return Response({'short-link': full_url})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_cart(request):
    cart_items = request.user.shop_cart.select_related('recipe')
    if not cart_items.exists():
        return Response({'error': 'Корзина пуста'}, 
                        status=status.HTTP_400_BAD_REQUEST)

    content = []
    for item in cart_items:
        recipe = item.recipe
        content.append(f'-- {recipe.name}')
        content.append('Ингредиенты:')
        for ingredient in recipe.recipe_ingredient.all():
            content.append(
                f'- {ingredient.ingredient.name}: {ingredient.amount} '
                f'{ingredient.ingredient.measurement_unit}')
        content.append('')

    response = HttpResponse('\n'.join(content), content_type='text/plain')
    return response


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_shopping_cart(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == 'POST':
        if request.user.shop_cart.filter(recipe=recipe).exists():
            return Response({'error': 'Рецепт уже в корзине'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeMiniSerializer(recipe, 
                                          context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    cart_item = request.user.shop_cart.filter(recipe=recipe)
    if not cart_item.exists():
        return Response({'error': 'Рецепт не в корзине'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    cart_item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def add_to_favorites(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == 'POST':
        if request.user.favorites.filter(recipe=recipe).exists():
            return Response({'error': 'Рецепт уже в избранном'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeMiniSerializer(recipe, 
                                          context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    favorite = request.user.favorites.filter(recipe=recipe)
    if not favorite.exists():
        return Response({'error': 'Рецепт не в избранном'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    favorite.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def ingredient_list(request):
    name_query = request.query_params.get('name')
    ingredients = Ingredients.objects.filter(
        name__istartswith=name_query
    ) if name_query else Ingredients.objects.all()
    serializer = IngredientSerializer(ingredients, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def ingredient_detail(request, id):
    ingredient = get_object_or_404(Ingredients, id=id)
    serializer = IngredientSerializer(ingredient)
    return Response(serializer.data)
