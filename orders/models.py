from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class OrderStatus(models.Model):
    """Статус заказа"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Название статуса")

    class Meta:
        verbose_name = "Статус заказа"
        verbose_name_plural = "Статусы заказов"
        ordering = ['name']

    def __str__(self):
        return self.name



class PickupPoint(models.Model):
    """Пункт выдачи"""
    address = models.CharField(max_length=300, unique=True, verbose_name="Адрес пункта выдачи")

    class Meta:
        verbose_name = "Пункт выдачи"
        verbose_name_plural = "Пункты выдачи"
        ordering = ['address']

    def __str__(self):
        return self.address


class Order(models.Model):
    """Заказ"""
    order_number = models.CharField(max_length=50, unique=True, verbose_name="Артикул заказа")
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, verbose_name="Статус заказа")
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.CASCADE, verbose_name="Адрес пункта выдачи")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    delivery_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата доставки")
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Клиент")
    pickup_code = models.CharField("Код для получения", max_length=50, blank=True, default="")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-order_date']

    def __str__(self):
        return f"Заказ {self.order_number}"


class OrderItem(models.Model):
    """Позиция в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.IntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"
        unique_together = ['order', 'product']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        """Общая стоимость позиции"""
        return self.quantity * self.price
