from django import forms
from django.core.exceptions import ValidationError
from PIL import Image

from .models import Product


class ProductForm(forms.ModelForm):
    """Форма для создания/редактирования товара"""

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'description', 'brand',
            'supplier', 'price', 'unit', 'quantity', 'discount', 'image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем подсказки к полям
        self.fields['price'].help_text = 'Цена в рублях'
        self.fields['discount'].help_text = 'Скидка в процентах (0-100)'
        self.fields['quantity'].help_text = 'Количество на складе (не может быть отрицательным)'
        self.fields['image'].help_text = 'Изображение товара (опционально)'
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image

        try:
            img = Image.open(image)
            width, height = img.size
        except Exception:
            raise ValidationError('Не удалось прочитать изображение. Загрузите файл изображения.')

        if width > 300 or height > 200:
            raise ValidationError('Изображение должно быть не больше 300×200 пикселей.')

        # важно: вернём курсор файла в начало
        image.seek(0)
        return image