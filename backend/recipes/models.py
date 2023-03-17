from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef, Value

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Мера веса'
    )

    class Meta():
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Тег')
    color = models.CharField(max_length=7, unique=True, verbose_name='Цвет')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Слаг')

    class Meta():
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class RecipQuerySet(models.QuerySet):
    def annotate_quryset(self, user):
        return self.annotate(
            is_favorited=Exists(Favorites.objects.filter(
                recipe__id=OuterRef('id'),
                user=user,
            )) if user.is_authenticated else Value(False),
            is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                recipe__id=OuterRef('id'),
                user=user,
            )) if user.is_authenticated else Value(False)
        )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        through_fields=('recipe', 'ingredient'),
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(max_length=200, blank=False, verbose_name='Рецепт')
    text = models.TextField(blank=False, verbose_name='Описание рецепта')
    image = models.ImageField(upload_to='images/', verbose_name='Картинка')
    cooking_time = models.PositiveIntegerField(
        validators=(
            MinValueValidator(1, message='Время должно быть больше 1 минуты'),
        ),
        verbose_name='Время приготовления',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    objects = RecipQuerySet.as_manager()

    class Meta():
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'Рецепт "{self.name}" автора "{self.author.username}"'


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveIntegerField(
        validators=(
            MinValueValidator(1, message='Количество должно быть больше 1 шт'),
        ),
        verbose_name='Количество',
    )

    class Meta():
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredient_recipe'
            )
        ]

    def __str__(self):
        return (f'В рецепте "{self.recipe.name}" - {self.amount} '
                f'{self.ingredient.measurement_unit} {self.ingredient.name}')


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta():
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorites_user_recipe'
            )
        ]

    def __str__(self):
        return f'Рецепт "{self.recipe.name}" в избранном {self.user.username}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta():
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart_user_recipe'
            )
        ]

    def __str__(self):
        return f'Рецепт "{self.recipe.name}" в корзине {self.user.username}'
