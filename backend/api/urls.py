from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, LoginView, LogoutView, RecipeViewSet,
                    TagViewSet, UserViewSet)

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', LoginView.as_view()),
    path('auth/token/logout/', LogoutView.as_view()),
]
