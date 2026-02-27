# Вариант 2: Книжный магазин

## Описание

Переделка базового проекта (магазин обуви) в книжный магазин. Студенты изменяют модели, формы, представления и шаблоны.

## Таблица переименований

| Было (обувь) | Стало (книги) |
|--------------|---------------|
| Product | Book |
| Category | Genre |
| Manufacturer | Publisher |
| Товар | Книга |
| Категория | Жанр |
| Производитель | Издательство |

---

## Часть 1. Настройка проекта (выполнить до изменений)

### Шаг 1.1. Создание виртуального окружения

```bash
python -m venv venv
```

---

### Шаг 1.2. Активация виртуального окружения

**Windows (PowerShell):**
```powershell
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

---

### Шаг 1.3. Установка зависимостей

```bash
pip install -r requirements.txt
```

---

### Шаг 1.4. Создание и применение миграций

Миграции в проекте отсутствуют — их нужно создать и применить:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Шаг 1.5. Создание суперпользователя

```bash
python manage.py createsuperuser
```

Введите логин (например: `admin`), email и пароль (например: `admin123`).

---

### Шаг 1.6. Регистрация моделей в админке

Откройте `products/admin.py`. Убедитесь, что зарегистрированы Supplier и Unit. Добавьте при необходимости:

```python
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation']
```

---

### Шаг 1.7. Добавление тестовых данных (до переименования моделей)

1. Запустите сервер: `python manage.py runserver`
2. Откройте http://127.0.0.1:8000/admin/
3. Добавьте **категории** (пока Category): Детектив, Фантастика, Роман, Учебная литература
4. Добавьте **производителей** (Manufacturer): Эксмо, АСТ, Питер, Дрофа
5. Добавьте **поставщиков**: Книготорг ООО, ОптКнига
6. Добавьте **единицы измерения**: штук (шт), упаковок (уп)
7. Добавьте 2–3 **товара** (Product) — они станут книгами после переименования

**Важно:** Выполните это до переименования моделей. После переименования моделей потребуется удалить миграции, `db.sqlite3` и создать миграции заново.

---

## Часть 2. Изменение моделей

### Шаг 2.1. Подготовка к переименованию

**Важно:** Переименование моделей потребует сброса базы данных и миграций.

1. Сохраните копию проекта (или зафиксируйте изменения в git)
2. Удалите файл `db.sqlite3`
3. Удалите все файлы миграций в `products/migrations/` и `orders/migrations/` **кроме** `__init__.py`:
   - Удалите `0001_initial.py` и другие файлы с номерами
   - Оставьте только `__init__.py` в каждой папке migrations

---

### Шаг 2.2. Переименование Category → Genre

1. Откройте `products/models.py`
2. Найдите класс `Category` и замените на:

```python
class Genre(models.Model):
    """Жанр книги"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название жанра")

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ['name']

    def __str__(self):
        return self.name
```

---

### Шаг 2.3. Переименование Author → Publisher

1. В том же файле найдите класс `Author` и замените на:

```python
class Publisher(models.Model):
    """Издательство"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название издательства")

    class Meta:
        verbose_name = "Издательство"
        verbose_name_plural = "Издательства"
        ordering = ['name']

    def __str__(self):
        return self.name
```

---

### Шаг 2.4. Переименование Product → Book

1. Найдите класс `Product` и замените на:

```python
class Book(models.Model):
    """Книга"""
    name = models.CharField(max_length=200, verbose_name="Название книги")
    category = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name="Жанр")
    description = models.TextField(blank=True, verbose_name="Описание")
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, verbose_name="Издательство")
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
        verbose_name="Обложка книги"
    )

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        if self.discount > 0:
            return self.price * (1 - self.discount / 100)
        return self.price

    @property
    def is_available(self):
        return self.quantity > 0
```

**Важно:** Поле `manufacturer` переименовывается в `publisher` — обновите все ссылки.

---

### Шаг 2.5. Обновление orders/models.py

1. Откройте `orders/models.py`
2. Замените импорт:
   ```python
   from products.models import Product
   ```
   на:
   ```python
   from products.models import Book
   ```
3. В классе `OrderItem` замените:
   ```python
   product = models.ForeignKey(Product, ...)
   ```
   на:
   ```python
   product = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
   ```
4. В методе `__str__` замените `self.product.name` — оставьте как есть (Book тоже имеет `name`)

---

### Шаг 2.6. Создание и применение миграций

```bash
python manage.py makemigrations products
python manage.py migrate
```

---

## Часть 3. Изменение форм

### Шаг 3.1. Обновление products/forms.py

1. Откройте `products/forms.py`
2. Замените импорт:
   ```python
   from .models import Product
   ```
   на:
   ```python
   from .models import Book
   ```
3. Замените класс и Meta:
   ```python
   class BookForm(forms.ModelForm):
       """Форма для создания/редактирования книги"""

       class Meta:
           model = Book
           fields = [
               'name', 'category', 'description', 'publisher',
               'supplier', 'price', 'unit', 'quantity', 'discount', 'image'
           ]
           widgets = {
               'name': forms.TextInput(attrs={'class': 'form-control'}),
               'category': forms.Select(attrs={'class': 'form-control'}),
               'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
               'publisher': forms.Select(attrs={'class': 'form-control'}),
               'supplier': forms.Select(attrs={'class': 'form-control'}),
               'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
               'unit': forms.Select(attrs={'class': 'form-control'}),
               'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
               'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
               'image': forms.FileInput(attrs={'class': 'form-control'}),
           }
   ```
4. В `__init__` замените `self.fields['price'].help_text` и др. — замените «товар» на «книгу» в подсказках

---

## Часть 4. Изменение views

### Шаг 4.1. Обновление products/views.py

1. Откройте `products/views.py`
2. Замените импорты:
   ```python
   from .models import Book, Genre, Publisher, Supplier
   from .forms import BookForm
   ```
3. Замените все вхождения:
   - `Product` → `Book`
   - `Category` → `Genre`
   - `Author` → `Publisher`
   - `ProductForm` → `BookForm`
   - `manufacturer` → `publisher` (в фильтрах и поиске)
4. В поиске замените `manufacturer__name` на `publisher__name` (если используется)
5. Сохраните файл

---

## Часть 5. Изменение admin

### Шаг 5.1. Обновление products/admin.py

1. Откройте `products/admin.py`
2. Замените импорты:
   ```python
   from products.models import Genre, Book, Publisher, Supplier, Unit
   ```
3. Замените регистрации:
   ```python
   @admin.register(Book)
   class BookAdmin(admin.ModelAdmin):
       ...

   @admin.register(Genre)
   class GenreAdmin(admin.ModelAdmin):
       ...

   @admin.register(Publisher)
   class PublisherAdmin(admin.ModelAdmin):
       ...
   ```

---

## Часть 6. Изменение шаблонов

### Шаг 6.1. templates/base/base.html

1. Откройте `templates/base/base.html`
2. Найдите строку:
   ```html
   <i class="bi bi-shop"></i> Магазин обуви
   ```
3. Замените на:
   ```html
   <i class="bi bi-book"></i> Книжный магазин
   ```
4. Найдите:
   ```html
   <i class="bi bi-list-ul"></i> Товары
   ```
5. Замените на:
   ```html
   <i class="bi bi-list-ul"></i> Книги
   ```

---

### Шаг 6.2. templates/products/product_list.html

1. Откройте `templates/products/product_list.html`
2. Замените заголовок:
   ```html
   <h1><i class="bi bi-list-ul"></i> Список книг</h1>
   ```
3. Замените кнопку:
   ```html
   <i class="bi bi-plus-circle"></i> Добавить книгу
   ```
4. Замените в таблице заголовок «Категория» на «Жанр», «Производитель» на «Издательство»
5. Замените переменную `product` на `book` в цикле:
   ```html
   {% for book in page_obj %}
   ```
   Важно: `{{ product.author.name }}` замените на `{{ book.publisher.name }}` (издательство)
6. Обновите URL-ы: `products:product_create` → оставьте как есть (если имена URL не менялись)
7. Замените `product.pk` на `book.pk` в ссылках редактирования/удаления

**Важно:** Имена URL в `products/urls.py` могут остаться `product_list`, `product_create` и т.д. — менять не обязательно.

---

## Часть 7. Обновление orders (если используется OrderItem)

В `orders/models.py` поле `product` ссылается на `Book`. В шаблонах заказов замените `product` на `book` при отображении.

---

## Часть 8. Добавление тестовых данных (после изменений)

1. Запустите: `python manage.py runserver`
2. Откройте http://127.0.0.1:8000/admin/
3. Добавьте **жанры**: Детектив, Фантастика, Роман
4. Добавьте **издательства**: Эксмо, АСТ, Питер
5. Добавьте **поставщиков** и **единицы измерения**
6. Добавьте **книги** с названиями, жанрами, издательствами

---

## Чек-лист выполнения

- [ ] Category → Genre
- [ ] Manufacturer → Publisher
- [ ] Product → Book
- [ ] Обновлены forms.py, views.py, admin.py
- [ ] Обновлён orders/models.py
- [ ] Обновлены шаблоны base.html и product_list.html
- [ ] Миграции применены
- [ ] Проект запускается без ошибок
- [ ] Добавлены тестовые данные (книги)
- [ ] Список книг отображается корректно
