import re
from datetime import datetime

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Booking, Review, Room

INPUT_CLASS = (
    'w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm '
    'text-slate-800 shadow-sm placeholder:text-slate-400 transition '
    'focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/15'
)
SELECT_CLASS = INPUT_CLASS + ' cursor-pointer'


class RegistrationForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Латиница и цифры, от 6 символов',
            'autocomplete': 'username',
        }),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Минимум 8 символов',
            'autocomplete': 'new-password',
        }),
    )
    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Повторите пароль',
            'autocomplete': 'new-password',
        }),
    )
    first_name = forms.CharField(
        label='Имя',
        max_length=150,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS}),
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=150,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': INPUT_CLASS}),
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': '+7 (999) 123-45-67',
        }),
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if len(username) < 6:
            raise ValidationError('Логин должен содержать минимум 6 символов.')
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            raise ValidationError('Логин может содержать только латинские буквы и цифры.')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        if len(password) < 8:
            raise ValidationError('Пароль должен содержать минимум 8 символов.')
        return password

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        password_confirm = cleaned.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Пароли не совпадают.')
        return cleaned


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'autocomplete': 'username',
        }),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'autocomplete': 'current-password',
        }),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get('username', '').strip()
        password = cleaned.get('password', '')
        if username and password:
            user = authenticate(self.request, username=username, password=password)
            if user is None:
                raise ValidationError('Неверный логин или пароль. Проверьте введённые данные.')
            self.user = user
        return cleaned


class BookingForm(forms.ModelForm):
    date_str = forms.CharField(
        label='Дата (дд.мм.гггг)',
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'дд.мм.гггг',
        }),
    )
    time_str = forms.CharField(
        label='Время (чч:мм)',
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'чч:мм',
        }),
    )

    class Meta:
        model = Booking
        fields = ['room', 'payment_method']
        widgets = {
            'room': forms.Select(attrs={'class': SELECT_CLASS}),
            'payment_method': forms.Select(attrs={'class': SELECT_CLASS}),
        }
        labels = {
            'room': 'Помещение',
            'payment_method': 'Способ оплаты',
        }

    def __init__(self, *args, room_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(is_active=True)
        if room_id:
            self.fields['room'].initial = room_id

    def clean_date_str(self):
        value = self.cleaned_data['date_str'].strip()
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValidationError('Укажите дату в формате дд.мм.гггг.')
        return value

    def clean_time_str(self):
        value = self.cleaned_data['time_str'].strip()
        try:
            datetime.strptime(value, '%H:%M')
        except ValueError:
            raise ValidationError('Укажите время в формате чч:мм.')
        return value

    def clean(self):
        cleaned = super().clean()
        date_str = cleaned.get('date_str')
        time_str = cleaned.get('time_str')
        room = cleaned.get('room')
        if date_str and time_str and room:
            start = datetime.strptime(
                f'{date_str} {time_str}', '%d.%m.%Y %H:%M'
            )
            cleaned['start_datetime'] = timezone.make_aware(start)
            overlap = Booking.objects.filter(
                room=room,
                start_datetime=start,
            ).exclude(
                status=Booking.STATUS_COMPLETED,
            )
            if self.instance.pk:
                overlap = overlap.exclude(pk=self.instance.pk)
            if overlap.exists():
                raise ValidationError(
                    'На выбранное время зал уже забронирован. Выберите другую дату или время.'
                )
        return cleaned

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        instance.start_datetime = self.cleaned_data['start_datetime']
        if user:
            instance.user = user
        if commit:
            instance.save()
        return instance


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': INPUT_CLASS + ' min-h-[100px] resize-y',
                'rows': 4,
                'placeholder': 'Опишите полученные услуги',
            }),
            'rating': forms.Select(
                choices=[(i, str(i)) for i in range(1, 6)],
                attrs={'class': SELECT_CLASS},
            ),
        }
        labels = {
            'text': 'Отзыв',
            'rating': 'Оценка',
        }
