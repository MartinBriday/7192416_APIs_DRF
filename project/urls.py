from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from shop.views import CategoryAPIView, ProductAPIView, CategoryViewSet, ProductViewSet, ArticleViewSet, \
    AdminCategoryViewSet, AdminArticleViewSet

router = routers.SimpleRouter()

router.register("category", CategoryViewSet, basename="category")
router.register("product", ProductViewSet, basename="product")
router.register("article", ArticleViewSet, basename="article")

router.register("admin/category", AdminCategoryViewSet, basename="admin-category")
router.register("admin/article", AdminArticleViewSet, basename="admin-article")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    # path('api/category/', CategoryAPIView.as_view()),
    # path('api/product/', ProductAPIView.as_view())
    path("api/", include(router.urls))
]
