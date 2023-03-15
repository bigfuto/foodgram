from django.contrib import admin
from .models import (
    Tag, Recipe, Ingredient, IngredientInRecipe, ShoppingCart,
    Favorites
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'text', 'count_favorites')
    search_fields = ('name', 'author', 'tags')
    list_filter = ('name', 'author', 'tags',)
    empy_value_display = '-пусто-'

    def count_favorites(self, obj):
        return obj.favorites.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empy_value_display = '-пусто-'


admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientInRecipe)
admin.site.register(ShoppingCart)
admin.site.register(Favorites)
