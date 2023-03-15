from rest_framework import serializers
from rest_framework.validators import ValidationError
from django.db import transaction
from .utils import Base64ImageField
from users.models import User, Subscription
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    ShoppingCart,
    Favorites,
    IngredientInRecipe
)


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
        ]

    def validate(self, data):
        email_exists = User.objects.filter(email=data["email"]).exists()
        if email_exists:
            raise ValidationError('С этим email уже существует пользователь')
        return super().validate(data)

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(SignUpSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.author.filter(
            subscriber=user
        ).exists()

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            'is_subscribed'
        ]


class RecipeFavoriteCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time',
        ]


class UserSubscribeSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(read_only=True)
    recipes_count = serializers.SerializerMethodField()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        recipes = obj.recipes.all()[:recipes_limit]
        return RecipeFavoriteCartSerializer(
            recipes, many=True, context=self.context
        ).data

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ['author', 'subscriber']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'color',
            'slug',
        ]


class IngridientsInRecipeSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = IngredientInRecipe
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount',
        ]


class IngridientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit',
        ]


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False)
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    def get_ingredients(self, obj):
        return IngridientsInRecipeSerializer(
            IngredientInRecipe.objects.filter(recipe=obj).all(), many=True
        ).data

    class Meta:
        model = Recipe
        fields = [
            'author',
            'id',
            'name',
            'text',
            'image',
            'cooking_time',
            'tags',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
        ]


class IngridientsInRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    amount = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = [
            'id',
            'recipe',
            'amount',
        ]


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngridientsInRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if tags:
            instance.tags.set(tags)
        if ingredients:
            instance.ingredients.clear()
        self._create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def _create_ingredients(self, ingredients, recipe):
        recipe_ingredients = [IngredientInRecipe(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount'],
        ) for ingredient in ingredients]
        IngredientInRecipe.objects.bulk_create(recipe_ingredients)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data

    class Meta:
        model = Recipe
        fields = [
            'author',
            'name',
            'text',
            'image',
            'cooking_time',
            'tags',
            'ingredients',
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = [
            'user',
            'recipe',
        ]


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorites
        fields = [
            'user',
            'recipe',
        ]
