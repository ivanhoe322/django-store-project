from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # встроенные урлы Django auth: /accounts/login/, /accounts/logout/ и т.д.
    path("accounts/", include("django.contrib.auth.urls")),

    # каталог
    path("products/", include("products.urls")),

    # главная = логин-страница (сделаем её в accounts)
    path("", include("accounts.urls")),
]