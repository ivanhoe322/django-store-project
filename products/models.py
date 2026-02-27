from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """Категория товара"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name


class Brand(models.Model):
    """Бренд товара"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название бренда")

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        ordering = ['name']

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Поставщик товара"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название поставщика")

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"
        ordering = ['name']

    def __str__(self):
        return self.name


class Unit(models.Model):
    """Единица измерения"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Единица измерения")
    abbreviation = models.CharField(max_length=10, blank=True, verbose_name="Сокращение")

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар"""
    sku = models.CharField("Артикул", max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=200, verbose_name="Название товара")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    description = models.TextField(blank=True, verbose_name="Описание")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Бренд")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="Поставщик")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Цена"
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="Единица измерения")
    quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Количество на складе"
    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Скидка (%)"
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name="Изображение товара"
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        """Расчетная цена с учетом скидки"""
        if self.discount > 0:
            return self.price * (1 - self.discount / 100)
        return self.price

    @property
    def is_available(self):
        """Проверка доступности товара"""
        return self.quantity > 0
