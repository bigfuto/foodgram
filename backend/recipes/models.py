from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

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


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
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
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

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
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
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
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='shopping_cart',
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
