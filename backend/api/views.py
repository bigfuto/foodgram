from django.contrib.auth import authenticate
from rest_framework import status, permissions, viewsets, mixins
from django.http import HttpResponse
# from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.validators import ValidationError
from django.db.models import Exists, OuterRef, Value, Sum
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from django.conf import settings
from .pagination import RecipePagination
from users.models import Subscription, User
from .permissions import IsAuthorOrReadOnly
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorites,
    ShoppingCart,
    IngredientInRecipe
)
from .serializers import (
    SignUpSerializer,
    UserSerializer,
    PasswordSerializer,
    SubscribeSerializer,
    UserSubscribeSerializer,
    TagSerializer,
    IngridientsSerializer,
    RecipeSerializer,
    FavoriteSerializer,
    RecipeFavoriteCartSerializer,
    ShoppingCartSerializer,
    RecipeCreateUpdateSerializer
)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            if not Token.objects.filter(user=user).exists():
                Token.objects.create(user=user)
            response = {'auth_token': user.auth_token.key}
            return Response(data=response, status=status.HTTP_201_CREATED)
        else:
            return Response(data={'message': 'Неверный email или пароль'})


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user is not None:
            request.user.auth_token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(data={'message': 'Пользователь не авторизван'})


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action in ('me', 'set_password', 'subscribe', 'subscriptions'):
            return [permissions.IsAuthenticated()]
        if self.action == 'destroy':
            return [IsAuthorOrReadOnly]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SignUpSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if user.check_password(serializer.data.get('current_password')):
            new_password = serializer.data.get('new_password')
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            data={'message': 'Текущий пароль не совпадает'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk):
        data = {'author': pk, 'subscriber': request.user.id}
        author = User.objects.filter(pk=pk).first()
        subscriber = request.user
        print(request.method)
        if request.method == 'POST':
            print(data)
            serializer = SubscribeSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = UserSerializer(
                instance=author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            Subscription.objects.filter(
                author=author, subscriber=subscriber
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        params = request.query_params.get(
            'recipes_limit',
            settings.DEFAULT_PAGE_SIZE,
        )
        context = self.get_serializer_context()
        try:
            context['recipes_limit'] = int(params)
        except ValueError:
            raise ValidationError({'message': 'recipes_limit не число'})
        queryset = self.get_queryset()
        queryset = queryset.filter(
            author__subscriber=request.user
        ).all()
        page = self.paginate_queryset(queryset=queryset)
        serializer = UserSubscribeSerializer(
            page,
            context=context,
            many=True
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngridientsSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset.all()


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = RecipePagination

    def get_permissions(self):
        if self.action in (
            'shopping_cart',
            'favorite',
            'download_shopping_cart'
        ):
            return [permissions.IsAuthenticated()]
        if self.action == 'destroy':
            return [IsAuthorOrReadOnly]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'shopping_cart':
            return ShoppingCartSerializer
        if self.action == 'favorite':
            return FavoriteSerializer
        if self.request.method in ('POST', 'PATCH'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def get_queryset(self):
        user = self.request.user
        tags = self.request.query_params.getlist('tags')
        author = self.request.query_params.get('author')
        queryset = Recipe.objects.select_related('author').prefetch_related(
            'tags', 'ingredients').annotate(
                is_favorited=Exists(Favorites.objects.filter(
                    recipe__id=OuterRef('id'),
                    user=user,
                )) if user.is_authenticated else Value(False),
                is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                    recipe__id=OuterRef('id'),
                    user=user,
                )) if user.is_authenticated else Value(False)
        )
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        if self.request.query_params.get('is_in_shopping_cart'):
            queryset = queryset.filter(is_in_shopping_cart=True)
        if self.request.query_params.get('is_favorited'):
            queryset = queryset.filter(is_favorited=True)
        if author:
            queryset = queryset.filter(author=author)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        return self._shopping_cart_favoite(pk, ShoppingCart)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        return self._shopping_cart_favoite(pk, Favorites)

    def _shopping_cart_favoite(self, pk, Klass):
        data = {'recipe': pk, 'user': self.request.user.id}
        item = Recipe.objects.filter(pk=data['recipe']).first()
        user = self.request.user
        if self.request.method == 'POST':
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                data=RecipeFavoriteCartSerializer(instance=item).data,
                status=status.HTTP_201_CREATED
            )
        elif self.request.method == 'DELETE':
            Klass.objects.filter(user=user, recipe=item).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        name = 'ingredient__name'
        unit = 'ingredient__measurement_unit'
        ingredients = IngredientInRecipe.objects.select_related(
            'recipe',
            'ingredient',
        ).filter(recipe__shopping_cart__user=request.user)
        ingredients = ingredients.values(
            name,
            unit,
        ).annotate(total=Sum('amount')).order_by('-total')
        catalog = '\n'.join(f'{item[name]} - {item["total"]} {item[unit]}'
                            for item in ingredients) + settings.FILE_MESSAGE
        response = HttpResponse(catalog, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="text.txt"'
        return response
