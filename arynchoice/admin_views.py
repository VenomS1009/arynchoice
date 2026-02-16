from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, CoinTransaction

@user_passes_test(lambda u: u.is_superuser)
def manage_coins(request):
    """Страница управления Аринкойнами"""
    
    if request.method == 'POST':
        username = request.POST.get('username')
        coins = int(request.POST.get('coins', 0))
        action = request.POST.get('action')
        reason = request.POST.get('reason', 'Админ начисление')
        
        try:
            user = User.objects.get(username=username)
            profile = user.userprofile
            
            if action == 'add':
                profile.arincoins += coins
                message = f"✅ Добавлено {coins} Аринкойнов пользователю {username}"
                
            elif action == 'set':
                profile.arincoins = coins
                message = f"✅ Установлено {coins} Аринкойнов пользователю {username}"
                
            elif action == 'subtract':
                profile.arincoins = max(0, profile.arincoins - coins)
                message = f"✅ Списано {coins} Аринкойнов у пользователя {username}"
                coins = -coins  # Для лога
            
            profile.save()
            
            # Логируем операцию
            CoinTransaction.objects.create(
                user=user,
                amount=coins,
                balance_after=profile.arincoins,
                reason=reason,
                admin=request.user
            )
            
            messages.success(request, message)
            
        except User.DoesNotExist:
            messages.error(request, f"❌ Пользователь {username} не найден")
        
        return redirect('manage_coins')
    
    # Статистика
    total_coins = sum(p.arincoins for p in UserProfile.objects.all())
    avg_coins = total_coins / UserProfile.objects.count() if UserProfile.objects.count() > 0 else 0
    
    context = {
        'profiles': UserProfile.objects.all().select_related('user').order_by('-arincoins'),
        'total_coins': total_coins,
        'avg_coins': round(avg_coins, 1),
        'users_count': UserProfile.objects.count(),
        'transactions': CoinTransaction.objects.all().select_related('user')[:10],
    }
    
    return render(request, 'admin/manage_coins.html', context)

@user_passes_test(lambda u: u.is_superuser)
def add_coins_bulk(request):
    """Массовое начисление Аринкойнов"""
    
    if request.method == 'POST':
        users = User.objects.all()
        coins = int(request.POST.get('coins', 0))
        reason = request.POST.get('reason', 'Массовое начисление')
        
        count = 0
        for user in users:
            profile = user.userprofile
            profile.arincoins += coins
            profile.save()
            
            CoinTransaction.objects.create(
                user=user,
                amount=coins,
                balance_after=profile.arincoins,
                reason=reason,
                admin=request.user
            )
            count += 1
        
        messages.success(request, f"✅ Начислено по {coins} Аринкойнов {count} пользователям")
        return redirect('manage_coins')
    
    return render(request, 'admin/add_coins_bulk.html')