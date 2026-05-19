from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .forms import BookingForm, LoginForm, RegistrationForm, ReviewForm
from .models import Booking, Review, Room, UserProfile


def home(request):
    login_form = LoginForm(request=request)
    register_form = RegistrationForm()
    show_login = False
    show_register = False

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'login':
            login_form = LoginForm(request=request, data=request.POST)
            show_login = True
            if login_form.is_valid():
                login(request, login_form.user)
                messages.success(request, f'Добро пожаловать, {login_form.user.first_name}!')
                return redirect(request.GET.get('next') or 'profile')
        elif action == 'register':
            register_form = RegistrationForm(request.POST)
            show_register = True
            if register_form.is_valid():
                data = register_form.cleaned_data
                user = User.objects.create_user(
                    username=data['username'],
                    password=data['password'],
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                )
                UserProfile.objects.create(user=user, phone=data['phone'])
                login(request, user)
                messages.success(request, 'Регистрация прошла успешно!')
                return redirect('profile')

    return render(request, 'home.html', {
        'login_form': login_form,
        'register_form': register_form,
        'show_login': show_login,
        'show_register': show_register,
    })


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('home')


@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user).select_related('room', 'review')
    review_forms = {}
    for booking in bookings:
        if booking.can_leave_review:
            review_forms[booking.pk] = ReviewForm()

    if request.method == 'POST' and request.POST.get('action') == 'review':
        booking = get_object_or_404(
            Booking, pk=request.POST.get('booking_id'), user=request.user
        )
        if not booking.can_leave_review:
            messages.error(request, 'Отзыв можно оставить только после завершения мероприятия.')
            return redirect('profile')
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.user = request.user
            review.save()
            messages.success(request, 'Спасибо за отзыв!')
            return redirect('profile')
        review_forms[booking.pk] = form

    booking_items = []
    for booking in bookings:
        booking_items.append({
            'booking': booking,
            'review_form': review_forms.get(booking.pk),
        })

    return render(request, 'profile.html', {
        'booking_items': booking_items,
    })


@login_required
def booking_create(request):
    room_id = request.GET.get('room')
    initial = {}
    if room_id:
        initial['room'] = room_id
    date_prefill = request.GET.get('date')
    time_prefill = request.GET.get('time')

    if request.method == 'POST':
        form = BookingForm(request.POST, room_id=room_id)
        if form.is_valid():
            booking = form.save(user=request.user)
            messages.success(request, f'Заявка #{booking.pk} успешно создана.')
            return redirect('profile')
    else:
        form = BookingForm(room_id=room_id, initial=initial)
        if date_prefill:
            form.fields['date_str'].initial = date_prefill
        if time_prefill:
            form.fields['time_str'].initial = time_prefill

    return render(request, 'booking_create.html', {'form': form})


@login_required
def halls(request):
    rooms = Room.objects.filter(is_active=True)
    selected_room_id = request.GET.get('room')
    selected_room = None
    if selected_room_id:
        selected_room = get_object_or_404(Room, pk=selected_room_id, is_active=True)

    return render(request, 'halls.html', {
        'rooms': rooms,
        'selected_room': selected_room,
    })


@login_required
@require_GET
def hall_availability(request, room_id):
    room = get_object_or_404(Room, pk=room_id, is_active=True)
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))

    start = timezone.make_aware(datetime(year, month, 1))
    if month == 12:
        end = timezone.make_aware(datetime(year + 1, 1, 1))
    else:
        end = timezone.make_aware(datetime(year, month + 1, 1))

    bookings = Booking.objects.filter(
        room=room,
        start_datetime__gte=start,
        start_datetime__lt=end,
    ).exclude(status=Booking.STATUS_COMPLETED)

    occupied = {}
    for b in bookings:
        day = b.start_datetime.strftime('%Y-%m-%d')
        time_slot = b.start_datetime.strftime('%H:%M')
        occupied.setdefault(day, []).append(time_slot)

    return JsonResponse({
        'room_id': room.id,
        'room_name': room.name,
        'year': year,
        'month': month,
        'occupied': occupied,
    })


def staff_check(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(staff_check, login_url='home')
def admin_panel(request):
    status_filter = request.GET.get('status', '')
    room_filter = request.GET.get('room', '')
    sort = request.GET.get('sort', '-created_at')
    search = request.GET.get('q', '')

    allowed_sorts = {
        'created_at': 'created_at',
        '-created_at': '-created_at',
        'start_datetime': 'start_datetime',
        '-start_datetime': '-start_datetime',
        'status': 'status',
    }
    order = allowed_sorts.get(sort, '-created_at')

    qs = Booking.objects.select_related('user', 'room', 'review')
    if status_filter:
        qs = qs.filter(status=status_filter)
    if room_filter:
        qs = qs.filter(room_id=room_filter)
    if search:
        qs = qs.filter(
            Q(user__username__icontains=search)
            | Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(room__name__icontains=search)
        )
    qs = qs.order_by(order)

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('status')
        booking = get_object_or_404(Booking, pk=booking_id)
        valid_statuses = {s[0] for s in Booking.STATUS_CHOICES}
        if new_status in valid_statuses:
            booking.status = new_status
            booking.save()
            messages.success(
                request,
                f'Статус заявки #{booking.pk} изменён на «{booking.get_status_display()}».',
            )
        return redirect(request.get_full_path() or 'admin_panel')

    return render(request, 'admin_panel.html', {
        'page_obj': page_obj,
        'rooms': Room.objects.all(),
        'status_filter': status_filter,
        'room_filter': room_filter,
        'sort': sort,
        'search': search,
        'status_choices': Booking.STATUS_CHOICES,
    })
