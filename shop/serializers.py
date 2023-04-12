
from rest_framework.serializers import ModelSerializer, SerializerMethodField, ValidationError

from shop.models import Category, Product, Article


class ArticleSerializer(ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "name", "price", "date_created", "date_updated", "product"]

    def validate_price(self, value):
        if value < 1:
            raise ValidationError("The article price must be greater than 1€ (your price set : {}.".format(value))
        return value
    def validate_product(self, value):
        if not value.active:
            raise ValidationError("The associated product ({}) must be active.".format(value.name))
        return value


class ProductListSerializer(ModelSerializer):

    class Meta:
        model = Product
        fields = ["id", "name", "date_created", "date_updated", "category"]


class ProductDetailSerializer(ModelSerializer):

    articles = SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "date_created", "date_updated", "category", "articles", "ecoscore"]

    def get_articles(self, instance):
        queryset = instance.articles.filter(active=True)
        serializer = ArticleSerializer(queryset, many=True)
        return serializer.data


class CategoryListSerializer(ModelSerializer):

    class Meta:
        model = Category
        fields = ["id", "name", "date_created", "date_updated"]

    def validate_name(self, value):
        if Category.objects.filter(name=value).exists():
            raise ValidationError("Category '{}' already exists.".format(value))
        return value

    def validate(self, data):
        if data["name"] not in data["description"]:
            raise ValidationError("Name ({}) must be in description".format(data["name"]))
        return data

class CategoryDetailSerializer(ModelSerializer):

    # products = ProductSerializer(many=True)
    products = SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "date_created", "date_updated", "products"]

    def get_products(self, instance):
        queryset = instance.products.filter(active=True)
        serializer = ProductDetailSerializer(queryset, many=True)
        return serializer.data
