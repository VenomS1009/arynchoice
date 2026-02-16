# arynchoice/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from .models import *
from .forms import RegisterForm
from .telegram_service import send_telegram_notification

# Функция home должна быть здесь
def home(request):
    """Главная страница"""
    # Если пользователь авторизован, перенаправляем на категории
    if request.user.is_authenticated:
        return redirect('categories')
    
    # Иначе показываем главную страницу
    return render(request, 'home.html')

def register(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Создаем профиль с Аринкойнами
            profile = user.userprofile
            profile.arincoins = 100  # Начальный бонус
            profile.save()
            
            login(request, user)
            messages.success(request, '🎉 Регистрация успешна! Вам начислено 100 Аринкойнов!')
            return redirect('categories')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    """Вход пользователя"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Добро пожаловать, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Неверное имя пользователя или пароль.")
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
    
    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """Выход пользователя"""
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, "Вы успешно вышли.")
    return redirect('home')

@login_required
def category_list(request):
    """Список категорий"""
    categories = Category.objects.all().order_by('order')
    return render(request, 'categories.html', {'categories': categories})

@login_required
def category_detail(request, category_id):
    """Детали категории с активностями"""
    category = get_object_or_404(Category, id=category_id)
    activities = category.activities.filter(is_available=True)
    return render(request, 'category_detail.html', {
        'category': category,
        'activities': activities
    })

@login_required
@transaction.atomic
def select_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id, is_available=True)
    profile = request.user.userprofile
    
    # Проверяем, достаточно ли Аринкойнов
    if profile.arincoins < activity.price:
        messages.error(request, f'❌ Недостаточно Аринкойнов! Нужно: {activity.price}, У тебя: {profile.arincoins}')
        return redirect('category_detail', category_id=activity.category.id)
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        
        # 👇 УБИРАЕМ ПРОВЕРКУ НА УНИКАЛЬНОСТЬ
        # Просто создаем новый выбор
        selection = Selection.objects.create(
            user=request.user,
            activity=activity,
            notes=notes
        )
        
        # Списываем Аринкойны
        profile.arincoins -= activity.price
        profile.save()
        
        # Отправляем уведомление в Telegram
        send_telegram_notification(request.user, activity, notes)
        
        # Считаем, сколько раз выбрали эту активность
        count = Selection.objects.filter(user=request.user, activity=activity).count()
        
        messages.success(request, 
            f'🎉 Ты выбрала "{activity.name}"! '
            f'Списано {activity.price} Аринкойнов. '
            f'Это уже {count}-й раз! ❤️'
        )
        return redirect('my_selections')
    
    return render(request, 'select_activity.html', {
        'activity': activity,
        'profile': profile
    })

@login_required
def user_profile(request):
    """Профиль пользователя"""
    profile = request.user.userprofile
    selections = Selection.objects.filter(user=request.user).select_related('activity')
    
    total_spent = sum(sel.activity.price for sel in selections)
    
    return render(request, 'profile.html', {
        'profile': profile,
        'selections': selections,
        'total_spent': total_spent
    })

@login_required
def my_selections(request):
    """Мои выборы"""
    selections = Selection.objects.filter(user=request.user).select_related('activity', 'activity__category').order_by('-selected_at')
    
    # Статистика
    total_spent = sum(sel.activity.price for sel in selections)
    unique_activities = selections.values('activity').distinct().count()
    
    context = {
        'selections': selections,
        'total_spent': total_spent,
        'unique_activities': unique_activities,
    }
    return render(request, 'my_selections.html', context)

from .models import EarnMethod, EarnRequest
from .telegram_service import send_earn_notification

@login_required
def earn_page(request):
    """Страница заработка Аринкойнов"""
    methods = EarnMethod.objects.filter(is_active=True)
    
    # Заявки пользователя
    user_requests = EarnRequest.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Статистика
    total_earned = EarnRequest.objects.filter(
        user=request.user, 
        status='approved'
    ).aggregate(total=models.Sum('coins_awarded'))['total'] or 0
    
    pending_count = EarnRequest.objects.filter(
        user=request.user, 
        status='pending'
    ).count()
    
    context = {
        'methods': methods,
        'user_requests': user_requests,
        'total_earned': total_earned,
        'pending_count': pending_count,
    }
    return render(request, 'earn.html', context)

@login_required
def submit_earn_request(request, method_id):
    """Отправить заявку на заработок"""
    method = get_object_or_404(EarnMethod, id=method_id, is_active=True)
    
    if request.method == 'POST':
        proof_text = request.POST.get('proof_text', '')
        
        # Создаем заявку
        earn_request = EarnRequest.objects.create(
            user=request.user,
            method=method,
            proof_text=proof_text,
            status='pending'
        )
        
        # Отправляем уведомление в Telegram
        send_earn_notification(request.user, method, proof_text)
        
        messages.success(request, 
            f'✅ Заявка на "{method.name}" отправлена! '
            f'Я проверю и начислю {method.reward} Аринкойнов.'
        )
        return redirect('earn_page')
    
    return render(request, 'submit_earn_request.html', {'method': method})

@login_required
def my_earnings(request):
    """Мои заработки"""
    requests = EarnRequest.objects.filter(user=request.user).order_by('-created_at')
    
    total_earned = requests.filter(status='approved').aggregate(
        total=models.Sum('coins_awarded')
    )['total'] or 0
    
    context = {
        'requests': requests,
        'total_earned': total_earned,
    }
    return render(request, 'my_earnings.html', context)