def recipe_queryset_fiter(queryset, request):
    tags = request.query_params.getlist('tags')
    author = request.query_params.get('author')
    if tags:
        queryset = queryset.filter(tags__slug__in=tags).distinct()
    if request.query_params.get('is_in_shopping_cart'):
        queryset = queryset.filter(is_in_shopping_cart=True)
    if request.query_params.get('is_favorited'):
        queryset = queryset.filter(is_favorited=True)
    if author:
        queryset = queryset.filter(author=author)
    return queryset
