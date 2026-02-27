from django import forms
from django.contrib.auth.models import User
from .models import Order, OrderStatus, PickupPoint


class OrderForm(forms.ModelForm):
    """Форма для создания/редактирования заказа"""

    class Meta:
        model = Order
        fields = ['order_number', 'status', 'pickup_point', 'delivery_date', 'customer']
        widgets = {
            'order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'pickup_point': forms.Select(attrs={'class': 'form-control'}),
            'delivery_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'customer': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем подсказки к полям
        self.fields['order_number'].help_text = 'Уникальный артикул заказа'
        self.fields['delivery_date'].help_text = 'Дата и время доставки (опционально)'