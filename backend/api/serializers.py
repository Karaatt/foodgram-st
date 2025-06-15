from rest_framework import serializers
from recipes.models import Recipe, Ingredients, RecipeIngredient
from users.models import User
from drf_extra_fields.fields import Base64ImageField


class UserProfileSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "avatar",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def get_is_subscribed(self, obj):
        request = self.context["request"]
        if request and not request.user.is_anonymous:
            return obj.subscribers.filter(user=request.user).exists()
        return False

    def get_avatar(self, obj):
        request = self.context["request"]
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class RecipeMiniSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields


class AvatarUpdateSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)


class SubscriptionSerializer(UserProfileSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "avatar",
            "recipes_count",
            "recipes",
        )
        read_only_fields = fields

    def get_recipes(self, obj):
        request = self.context["request"]
        limit = request.query_params.get("recipes_limit")
        recipes = obj.recipes.all()
        if limit and limit.isdigit():
            recipes = recipes[: int(limit)]
        return RecipeMiniSerializer(
            recipes, many=True, context={"request": request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        request = self.context["request"]
        return (
            request.user.is_authenticated
            and obj.subscribers.filter(user=request.user).exists()
        )


class SubscribeCreateSerializer(serializers.Serializer):
    def validate(self, data):
        user = self.context["request"].user
        author = self.context["author"]
        if user == author:
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя."
            )
        if user.subscriptions.filter(author=author).exists():
            raise serializers.ValidationError(
                "Вы уже подписаны на этого автора."
            )
        return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ("id", "name", "measurement_unit")
        read_only_fields = fields


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientCreateSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
    )
    amount = serializers.IntegerField(min_value=1, max_value=32000)


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)
    ingredients = IngredientCreateSerializer(
        many=True, write_only=True, required=True
    )
    ingredients_read = RecipeIngredientSerializer(
        many=True, source="recipe_ingredient", read_only=True
    )
    image = Base64ImageField(required=True, allow_null=False)
    cooking_time = serializers.IntegerField(min_value=1, max_value=32000)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "ingredients_read",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        extra_kwargs = {
            "name": {"required": True},
            "text": {"required": True},
            "image": {"required": True},
        }

    def validate(self, data):
        if self.partial and "ingredients" not in data:
            raise serializers.ValidationError(
                {
                    "ingredients": (
                        "Поле ingredients " "обязательно для обновления."
                    )
                }
            )
        return data

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                "Поле image не может быть пустым."
            )
        return value

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                "Необходимо указать хотя бы один ингредиент."
            )
        ingredient_ids = [item["id"] for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться."
            )
        return ingredients

    def create_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient["id"],
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients_data
            ]
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        instance.recipe_ingredient.all().delete()
        self.create_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def get_is_favorited(self, obj):
        request = self.context["request"]
        return (
            request.user.is_authenticated
            and obj.favorited_by.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context["request"]
        return (
            request.user.is_authenticated
            and obj.in_cart.filter(user=request.user).exists()
        )

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipe_ingredient"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = fields

    def get_is_favorited(self, obj):
        request = self.context["request"]
        return (
            request.user.is_authenticated
            and obj.favorited_by.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context["request"]
        return (
            request.user.is_authenticated
            and obj.in_cart.filter(user=request.user).exists()
        )
