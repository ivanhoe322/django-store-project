from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Order, OrderStatus, PickupPoint
from .forms import OrderForm


def get_user_role(user):
    """Получение роли пользователя"""
    if user.is_superuser:
        return 'admin'
    if user.groups.filter(name='Менеджеры').exists():
        return 'manager'
    if user.groups.filter(name='Клиенты').exists():
        return 'client'
    return 'guest'


@login_required
def order_list(request):
    """Список заказов (для менеджеров и администраторов)"""
    user_role = get_user_role(request.user)

    if user_role not in ['manager', 'admin']:
        messages.error(request, 'У вас нет прав для просмотра заказов.')
        return redirect('products:product_list')

    # Для клиентов показываем только их заказы
    if user_role == 'client':
        orders = Order.objects.filter(customer=request.user).select_related(
            'status', 'pickup_point', 'customer'
        )
    else:
        # Для менеджеров и админов показываем все заказы
        orders = Order.objects.select_related('status', 'pickup_point', 'customer')

    orders = orders.order_by('-order_date')

    # Пагинация
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'user_role': user_role,
    }

    return render(request, 'orders/order_list.html', context)


@login_required
def order_create(request):
    """Создание нового заказа (только для администраторов)"""
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для выполнения этого действия.')
        return redirect('orders:order_list')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заказ успешно создан.')
            return redirect('orders:order_list')
    else:
        form = OrderForm()

    return render(request, 'orders/order_form.html', {
        'form': form,
        'title': 'Добавить заказ',
        'user_role': get_user_role(request.user)
    })


@login_required
def order_update(request, pk):
    """Редактирование заказа (только для администраторов)"""
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для выполнения этого действия.')
        return redirect('orders:order_list')

    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заказ успешно обновлен.')
            return redirect('orders:order_list')
    else:
        form = OrderForm(instance=order)

    return render(request, 'orders/order_form.html', {
        'form': form,
        'order': order,
        'title': 'Редактировать заказ',
        'user_role': get_user_role(request.user)
    })


@login_required
def order_delete(request, pk):
    """Удаление заказа (только для администраторов)"""
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для выполнения этого действия.')
        return redirect('orders:order_list')

    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Заказ успешно удален.')
        return redirect('orders:order_list')

    return render(request, 'orders/order_confirm_delete.html', {
        'order': order,
        'user_role': get_user_role(request.user)
    })
