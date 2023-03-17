from django.contrib import admin
from django.utils.html import mark_safe

from .models import (Favorites, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 2
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'text',
        'picture',
        'count_favorites'
    )
    search_fields = ('name', 'author', 'tags')
    list_filter = ('name', 'author', 'tags',)
    filter_gorizontal = ('tags',)
    empy_value_display = '-пусто-'
    inlines = (IngredientInline,)
    list_display_links = ('name',)

    def count_favorites(self, obj):
        return obj.favorites.count()

    def picture(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" hieght="80"')


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
