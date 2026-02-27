from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category, Brand, Supplier
from .forms import ProductForm


def get_user_role(user):
    """Получение роли пользователя"""
    if user.is_superuser:
        return 'admin'
    if user.groups.filter(name='Менеджеры').exists():
        return 'manager'
    if user.groups.filter(name='Клиенты').exists():
        return 'client'
    return 'guest'

# /products?search="test user"
def product_list(request):
    """Список товаров с учетом роли пользователя"""
    user_role = get_user_role(request.user) if request.user.is_authenticated else 'guest'

    # значения по умолчанию (чтобы не было UnboundLocalError)
    search_query = ''
    supplier_filter = ''
    sort_by = ''
    suppliers = Supplier.objects.all()  # чтобы шаблон мог строить выпадашку

    # базовый queryset
    products = Product.objects.select_related('category', 'brand', 'supplier', 'unit')

    # фильтры и поиск только для manager/admin
    if user_role in ['manager', 'admin']:
        # поиск
        search_query = request.GET.get('search', '').strip()
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(brand__name__icontains=search_query) |
                Q(supplier__name__icontains=search_query)
            )

        # фильтр по поставщику
        supplier_filter = request.GET.get('supplier', '').strip()
        if supplier_filter:
            products = products.filter(supplier__id=supplier_filter)

        # сортировка
        sort_by = request.GET.get('sort', '').strip()
        if sort_by == 'quantity_asc':
            products = products.order_by('quantity')
        elif sort_by == 'quantity_desc':
            products = products.order_by('-quantity')
        else:
            products = products.order_by('id')
            sort_by = ''
    else:
        # для гостя/клиента: просто стабильный порядок
        products = products.order_by('id')

    # пагинация
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'user_role': user_role,
        'suppliers': suppliers,
        'search_query': search_query,
        'supplier_filter': supplier_filter,
        'sort_by': sort_by,
    }
    return render(request, 'products/product_list.html', context)


@login_required
def product_create(request):
    """Создание нового товара (только для администраторов)"""
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для выполнения этого действия.')
        return redirect('main:product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно создан.')
            return redirect('main:product_list')
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Добавить товар',
        'user_role': get_user_role(request.user)
    })


@login_required
def product_update(request, pk):
    """Редактирование товара (только для администраторов)"""
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для выполнения этого действия.')
        return redirect('main:product_list')

    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # Удаляем старое изображение, если оно заменено
            if 'image' in request.FILES and product.image:
                product.image.delete()
            form.save()
            messages.success(request, 'Товар успешно обновлен.')
            return redirect('main:product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_form.html', {
        'form': form,
        'product': product,
        'title': 'Редактировать товар',
        'user_role': get_user_role(request.user)
    })


@login_required
def product_delete(request, pk):
    """Удаление товара (только для администраторов)"""
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для выполнения этого действия.')
        return redirect('main:product_list')

    product = get_object_or_404(Product, pk=pk)

    # Проверяем, используется ли товар в заказах
    if hasattr(product, 'orderitem_set') and product.orderitem_set.exists():
        messages.error(request, 'Невозможно удалить товар, который присутствует в заказах.')
        return redirect('main:product_list')

    if request.method == 'POST':
        # Удаляем изображение
        if product.image:
            product.image.delete()
        product.delete()
        messages.success(request, 'Товар успешно удален.')
        return redirect('main:product_list')

    return render(request, 'products/product_confirm_delete.html', {
        'product': product,
        'user_role': get_user_role(request.user)
    })
