from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User


MIN_VALUE = 1
MAX_VALUE = 32000


class Ingredients(models.Model):
    name = models.CharField('Название', max_length=128, 
                            default='неизвестно')
    measurement_unit = models.CharField('Единица измерения', 
                                        max_length=64, default='г')

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        related_name='recipes', 
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=256)
    image = models.ImageField('Изображение', upload_to='recipes/images/', 
                              null=True, blank=True)
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredients, through='RecipeIngredient', 
        related_name='recipes', verbose_name='Ингредиенты'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления', validators=[MinValueValidator(MIN_VALUE), 
                                           MaxValueValidator(MAX_VALUE)]
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, 
                               related_name='recipe_ingredient')
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(
        'Количество', validators=[MinValueValidator(MIN_VALUE), 
                                  MaxValueValidator(MAX_VALUE)]
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'ингредиенты в рецептах'

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, 
                               related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                             related_name='subscriptions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return f'{self.user.username} на {self.author.username}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                             related_name='shop_cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, 
                               related_name='in_cart')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'корзины'

    def __str__(self):
        return f'{self.recipe} в корзине {self.user}'
