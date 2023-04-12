import requests
from django.db import models, transaction


class Category(models.Model):

    objects = models.Manager()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=False)

    @transaction.atomic
    def disable(self):
        if not self.active:
            return
        self.active = False
        self.save()
        self.products.update(active=False)

    def __str__(self):
        return self.name


class Product(models.Model):

    objects = models.Manager()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=False)

    category = models.ForeignKey('shop.Category', on_delete=models.CASCADE, related_name='products')

    def call_external_api(self, method, url):
        return requests.request(method, url, verify=False)

    @property
    def ecoscore(self):
        response = self.call_external_api("GET", "https://world.openfoodfacts.org/api/v0/product/3229820787015.json")
        if response.status_code == 200:
            return response.json()["product"]["ecoscore_grade"]

    @transaction.atomic
    def disable(self):
        if not self.active:
            return
        self.active = False
        self.save()
        self.articles.update(active=False)


    def __str__(self):
        return self.name


class Article(models.Model):

    objects = models.Manager()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=4, decimal_places=2)

    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, related_name='articles')

    def __str__(self):
        return self.name
