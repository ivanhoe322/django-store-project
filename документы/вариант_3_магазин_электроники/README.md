# Вариант 3: Магазин электроники

## Описание

Переделка базового проекта (магазин обуви) в магазин электроники. Основное изменение — производитель (Manufacturer) становится брендом (Brand).

## Таблица переименований

| Было (обувь) | Стало (электроника) |
|--------------|---------------------|
| Product | Product (без изменений) |
| Category | Category (без изменений) |
| Manufacturer | Brand |
| Товар | Товар |
| Категория | Категория |
| Производитель | Бренд |

---

## Часть 1. Настройка проекта

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

### Шаг 1.4. Применение миграций

```bash
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

### Шаг 1.7. Добавление тестовых данных (до изменений)

1. Запустите: `python manage.py runserver`
2. Откройте http://127.0.0.1:8000/admin/
3. Добавьте **категории**: Смартфоны, Ноутбуки, Наушники, Планшеты
4. Добавьте **производителей** (Manufacturer): Apple, Samsung, Xiaomi, Sony, Huawei
5. Добавьте **поставщиков**: ТехноМаркет, ЭлектроОпт, ГаджетСервис
6. Добавьте **единицы измерения**: штук (шт), упаковок (уп)
7. Добавьте 2–3 **товара** (Product) — например: iPhone 15, Samsung Galaxy, Xiaomi Redmi

**Важно:** Эти данные будут сохранены. После переименования Manufacturer → Brand потребуется миграция. Django может предложить удалить старую таблицу и создать новую — в этом случае данные производителей будут потеряны, их нужно будет добавить заново как «Бренды».

---

## Часть 2. Изменение модели Manufacturer → Brand

### Шаг 2.1. Переименование класса Author в products/models.py

1. Откройте `products/models.py`
2. Найдите класс `Author`:

```python
class Author(models.Model):
    """Производитель товара"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название производителя")

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"
        ordering = ['name']

    def __str__(self):
        return self.name
```

3. Замените на:

```python
class Brand(models.Model):
    """Бренд товара"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название бренда")

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        ordering = ['name']

    def __str__(self):
        return self.name
```

4. Сохраните файл (Ctrl+S)

---

### Шаг 2.2. Изменение поля manufacturer → brand в модели Product

1. В том же файле найдите класс `Product`
2. Найдите строку:
   ```python
   manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name="Производитель")
   ```
3. Замените на:
   ```python
   brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Бренд")
   ```
4. Сохраните файл

---

### Шаг 2.3. Создание миграции

Выполните в терминале:

```bash
python manage.py makemigrations products
```

Django может спросить, переименовывать ли модель Author в Brand. Выберите вариант **«y»** (переименование), если он предлагается. Если Django создаёт новую таблицу и удаляет старую — данные производителей будут потеряны.

**Альтернатива (сохранение данных):** Создайте миграцию вручную:

```bash
python manage.py makemigrations products --empty
```

Затем отредактируйте созданный файл миграции и добавьте:

```python
operations = [
    migrations.RenameModel(old_name='Manufacturer', new_name='Brand'),
    migrations.RenameField(model_name='product', old_name='manufacturer_id', new_name='brand_id'),
]
```

---

### Шаг 2.4. Применение миграции

```bash
python manage.py migrate
```

---

## Часть 3. Изменение форм

### Шаг 3.1. Обновление products/forms.py

1. Откройте `products/forms.py`
2. В `fields` замените `'author'` на `'brand'`:
   ```python
   fields = [
       'name', 'category', 'description', 'brand',
       'supplier', 'price', 'unit', 'quantity', 'discount', 'image'
   ]
   ```
3. В `widgets` замените `'manufacturer'` на `'brand'`:
   ```python
   'brand': forms.Select(attrs={'class': 'form-control'}),
   ```
4. Удалите или обновите строку с `help_text` для `manufacturer`, если она есть
5. Сохраните файл

---

## Часть 4. Изменение views

### Шаг 4.1. Обновление products/views.py

1. Откройте `products/views.py`
2. Замените импорт:
   ```python
   from .models import Product, Category, Brand, Supplier
   ```
3. Найдите все вхождения `Author` и замените на `Brand`
4. Найдите все вхождения `author` и замените на `brand`:
   - В `select_related`: `'author'` → `'brand'`
   - В фильтрах поиска: `Q(author__name__icontains=...)` → `Q(brand__name__icontains=...)`
   - В `manufacturer__name` (если есть) → `brand__name`
5. Сохраните файл

---

## Часть 5. Изменение admin

### Шаг 5.1. Обновление products/admin.py

1. Откройте `products/admin.py`
2. Замените импорт:
   ```python
   from products.models import Category, Product, Brand, Supplier, Unit
   ```
3. Замените регистрацию:
   ```python
   @admin.register(Brand)
   class BrandAdmin(admin.ModelAdmin):
       list_display = ['name']
   ```
   (вместо `@admin.register(Manufacturer)`)
4. Сохраните файл

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
   <i class="bi bi-phone"></i> Магазин электроники
   ```
4. Сохраните файл

---

### Шаг 6.2. templates/products/product_list.html

1. Откройте `templates/products/product_list.html`
2. В заголовке таблицы найдите «Производитель» и замените на «Бренд»:
   ```html
   <th>Бренд</th>
   ```
3. В теле таблицы найдите:
   ```html
   <td>{{ product.manufacturer.name }}</td>
   ```
4. Замените на:
   ```html
   <td>{{ product.brand.name }}</td>
   ```
5. Сохраните файл

---

## Часть 7. Добавление тестовых данных (после изменений)

Если данные производителей были потеряны при миграции:

1. Запустите: `python manage.py runserver`
2. Откройте http://127.0.0.1:8000/admin/
3. В разделе **PRODUCTS** нажмите **Бренды** → **Добавить бренд**
4. Добавьте: Apple, Samsung, Xiaomi, Sony, Huawei
5. Откройте **Товары** и отредактируйте каждый товар — выберите бренд в поле «Бренд»
6. Сохраните изменения

---

## Часть 8. Проверка

1. Откройте http://127.0.0.1:8000/products/
2. Убедитесь, что:
   - В меню отображается «Магазин электроники»
   - В таблице товаров колонка называется «Бренд»
   - Названия брендов отображаются корректно
3. Войдите под суперпользователем и проверьте создание/редактирование товара — поле «Бренд» должно работать

---

## Чек-лист выполнения

- [ ] Manufacturer → Brand в models.py
- [ ] Product.manufacturer → Product.brand
- [ ] Миграции созданы и применены
- [ ] forms.py: manufacturer → brand
- [ ] views.py: Manufacturer → Brand, manufacturer → brand
- [ ] admin.py: Brand зарегистрирован
- [ ] base.html: «Магазин электроники»
- [ ] product_list.html: «Бренд», product.brand.name
- [ ] Добавлены бренды и привязаны к товарам
- [ ] Проект запускается без ошибок

---

## Файлы для редактирования

| Файл | Изменения |
|------|------------|
| `products/models.py` | Manufacturer → Brand, manufacturer → brand |
| `products/forms.py` | manufacturer → brand |
| `products/views.py` | Manufacturer → Brand, manufacturer → brand |
| `products/admin.py` | Manufacturer → Brand |
| `templates/base/base.html` | Название сайта |
| `templates/products/product_list.html` | Производитель → Бренд |
