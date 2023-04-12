from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from shop.models import Category, Product, Article
from shop.serializers import CategoryListSerializer, CategoryDetailSerializer, ProductListSerializer, ProductDetailSerializer, ArticleSerializer
from shop.permissions import IsAdminAuthenticated, IsStaffAuthenticated


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.detail_serializer_class is not None and self.action == "retrieve":
            return self.detail_serializer_class
        return super().get_serializer_class()


class CategoryAPIView(APIView):

    def get(self, *args, **kwargs):
        categories = Category.objects.all()
        serializer = CategoryDetailSerializer(categories, many=True)
        return Response(serializer.data)


class CategoryViewSet(MultipleSerializerMixin, ReadOnlyModelViewSet):

    serializer_class = CategoryListSerializer
    detail_serializer_class = CategoryDetailSerializer

    def get_queryset(self):
        queryset = Category.objects.filter(active=True)
        name = self.request.GET.get("name")
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset
        # return Category.objects.all()

    @action(detail=True, methods=['post'])
    def disable(self, request, pk):
        self.get_object().disable()
        return Response()


class AdminCategoryViewSet(MultipleSerializerMixin, ModelViewSet):

    serializer_class = CategoryListSerializer
    detail_serializer_class = CategoryDetailSerializer
    permission_classes = [IsAdminAuthenticated, IsStaffAuthenticated]

    def get_queryset(self):
        return Category.objects.all()


class ProductAPIView(APIView):

    def get(self, *args, **kwargs):
        products = Product.objects.all()
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(MultipleSerializerMixin, ReadOnlyModelViewSet):
    serializer_class = ProductListSerializer
    detail_serializer_class = ProductDetailSerializer

    def get_queryset(self):
        queryset = Product.objects.filter(active=True)
        category_id = self.request.GET.get("category_id")
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        return queryset
        # return Product.objects.all()

    @action(detail=True, methods=['post'])
    def disable(self, request, pk):
        self.get_object().disable()
        return Response()


class ArticleViewSet(MultipleSerializerMixin, ReadOnlyModelViewSet):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        queryset = Article.objects.filter(active=True)
        product_id = self.request.GET.get("product_id")
        if product_id is not None:
            queryset = queryset.filter(product_id=product_id)
        return queryset

class AdminArticleViewSet(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.all()

