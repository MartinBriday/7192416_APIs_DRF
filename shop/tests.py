from django.urls import reverse_lazy, reverse
from rest_framework.test import APITestCase
from unittest import mock

from shop.models import Category, Product
from shop.mocks import mock_openfoodfact_success, ECOSCORE_GRADE


class ShopAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Fruits', active=True)
        Category.objects.create(name='Légumes', active=False)

        cls.product = cls.category.products.create(name='Ananas', active=True)
        cls.category.products.create(name='Banane', active=False)

        cls.category_2 = Category.objects.create(name='Légumes', active=True)
        cls.product_2 = cls.category_2.products.create(name='Tomate', active=True)

    def format_datetime(self, value):
        # Cette méthode est un helper permettant de formater une date en chaine de caractères sous le même format que
        # celui de l’api
        return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def get_category_list_data(self, categories):
        return [
            {
                'id': category.id,
                'name': category.name,
                'date_created': self.format_datetime(category.date_created),
                'date_updated': self.format_datetime(category.date_updated)
            } for category in categories
        ]

    def get_category_detail_data(self, category):
        return {
            'id': category.id,
            'name': category.name,
            'date_created': self.format_datetime(category.date_created),
            'date_updated': self.format_datetime(category.date_updated),
            'products': [self.get_product_detail_data(product) for product in category.products.filter(active=True)]
        }

    def get_product_list_data(self, products):
        return [
            {
                'id': product.id,
                'name': product.name,
                'date_created': self.format_datetime(product.date_created),
                'date_updated': self.format_datetime(product.date_updated),
                'category': product.category_id,
            } for product in products
        ]

    def get_product_detail_data(self, product):
        return {
            'id': product.id,
            'name': product.name,
            'date_created': self.format_datetime(product.date_created),
            'date_updated': self.format_datetime(product.date_updated),
            'category': product.category_id,
            'articles': self.get_article_detail_data(product.articles.filter(active=True)),
            'ecoscore': ECOSCORE_GRADE
        }

    def get_article_detail_data(self, articles):
        return [
            {
                'id': article.id,
                'name': article.name,
                'date_created': self.format_datetime(article.date_created),
                'date_updated': self.format_datetime(article.date_updated),
                'category': article.product_id
            } for article in articles
        ]


class TestCategory(ShopAPITestCase):
    # Nous stockons l’url de l'endpoint dans un attribut de classe pour pouvoir l’utiliser plus facilement dans
    # chacun de nos tests
    url = reverse_lazy('category-list')

    def test_list(self):
        # Créons deux catégories dont une seule est active
        # category = Category.objects.create(name='Fruits', active=True)
        # Category.objects.create(name='Légumes', active=False)

        # On réalise l’appel en GET en utilisant le client de la classe de test
        response = self.client.get(self.url)
        # Nous vérifions que le status code est bien 200
        # et que les valeurs retournées sont bien celles attendues
        self.assertEqual(response.status_code, 200)
        # expected = [
        #     {
        #         'id': self.category.id,
        #         'name': self.category.name,
        #         'date_created': self.format_datetime(self.category.date_created),
        #         'date_updated': self.format_datetime(self.category.date_updated),
        #     }
        # ]
        self.assertEqual(self.get_category_list_data([self.category, self.category_2]), response.json()["results"])

    def test_detail(self):
        url_detail = reverse('category-detail', kwargs={'pk': self.category.pk})
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_category_detail_data(self.category), response.json())

    def test_create(self):
        # Nous vérifions qu’aucune catégorie n'existe avant de tenter d’en créer une
        # self.assertFalse(Category.objects.exists())
        category_count = Category.objects.count()
        response = self.client.post(self.url, data={'name': 'Nouvelle catégorie'})
        # Vérifions que le status code est bien en erreur et nous empêche de créer une catégorie
        self.assertEqual(response.status_code, 405)
        # Enfin, vérifions qu'aucune nouvelle catégorie n’a été créée malgré le status code 405
        # self.assertFalse(Category.objects.exists())
        self.assertEqual(Category.objects.count(), category_count)


class TestProduct(ShopAPITestCase):
    url = reverse_lazy("product-list")

    def test_list(self):
        # category = Category.objects.create(name='Fruits', active=True)
        # product = Product.objects.create(name="Pomme", active=True, category=category)
        # Product.objects.create(name="Poire", active=False, category=category)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_product_list_data([self.product, self.product_2]), response.json()["results"])

    @mock.patch("shop.models.Product.call_external_api", mock_openfoodfact_success)
    def test_detail(self):
        url_detail = reverse('product-detail', kwargs={'pk': self.product.pk})
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_product_detail_data(self.product), response.json())

    def test_list_filter(self):
        # category1 = Category.objects.create(name='Fruits', active=True)
        # product1 = Product.objects.create(name="Pomme", active=True, category=category1)
        # category2 = Category.objects.create(name='Légumes', active=True)
        # Product.objects.create(name="Carotte", active=True, category=category2)

        response = self.client.get(self.url + "?category_id={}".format(self.category.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_product_list_data([self.product]), response.json()["results"])

    def test_create(self):
        product_count = Product.objects.count()
        response = self.client.post(self.url, data={'name': 'Nouveau produit'})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Product.objects.count(), product_count)

    def test_delete(self):
        response = self.client.delete(reverse("product-detail", kwargs={"pk": self.product.id}))
        self.assertEqual(response.status_code, 405)
        self.product.refresh_from_db()
