from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from shop.views import CategoryAPIView, ProductAPIView

router = routers.SimpleRouter()

router.register("category", CategoryAPIView, basename="category")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    # path('api/category/', CategoryAPIView.as_view()),
    # path('api/product/', ProductAPIView.as_view())
    path("api/", include(router.urls))
]
