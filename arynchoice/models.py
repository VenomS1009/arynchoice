from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    arincoins = models.IntegerField(default=100, verbose_name="Аринкойны")
    is_special_user = models.BooleanField(default=False, verbose_name="Особый доступ")
    
    def __str__(self):
        return f"{self.user.username} - {self.arincoins} Аринкойнов"

# Сигналы для автоматического создания профиля
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(verbose_name="Описание")
    icon = models.CharField(max_length=50, default="fas fa-heart", 
                           verbose_name="Иконка (Font Awesome)")
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order']
    
    def __str__(self):
        return self.name

class Activity(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                                 related_name='activities')
    name = models.CharField(max_length=200, verbose_name="Название активности")
    description = models.TextField(verbose_name="Подробное описание")
    price = models.IntegerField(verbose_name="Стоимость в Аринкойнах")
    image = models.ImageField(upload_to='activities/', verbose_name="Картинка")
    duration = models.CharField(max_length=50, verbose_name="Продолжительность")
    location = models.CharField(max_length=200, verbose_name="Место")
    is_available = models.BooleanField(default=True, verbose_name="Доступно")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Активность"
        verbose_name_plural = "Активности"
    
    def __str__(self):
        return f"{self.name} - {self.price} Аринкойнов"

class Selection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    selected_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, verbose_name="Пожелания/комментарии")
    is_confirmed = models.BooleanField(default=False, verbose_name="Подтверждено")
    
    class Meta:
        verbose_name = "Выбор"
        verbose_name_plural = "Выборы"
        # unique_together = ['user', 'activity']
        ordering = ['-selected_at']
    
    def __str__(self):
        return f"{self.user.username} выбрал(а) {self.activity.name} - {self.selected_at}"   
    
class CoinTransaction(models.Model):
    """Модель для логов операций с Аринкойнами"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()  # Может быть положительным или отрицательным
    balance_after = models.IntegerField()
    reason = models.CharField(max_length=255)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='coin_operations')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
    
    def __str__(self):
        sign = '+' if self.amount >= 0 else ''
        return f"{self.user.username}: {sign}{self.amount} Аринкойнов ({self.reason})"

class Achievement(models.Model):
    """Модель для достижений/бонусов"""
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    coins_reward = models.IntegerField(verbose_name="Награда в Аринкойнах")
    icon = models.CharField(max_length=50, default="fas fa-trophy", verbose_name="Иконка")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    
    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'
    
    def __str__(self):
        return f"{self.name} (+{self.coins_reward} Аринкойнов)"   
    
class EarnMethod(models.Model):
    """Способы заработка Аринкойнов"""
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    reward = models.IntegerField(verbose_name="Награда в Аринкойнах")
    icon = models.CharField(max_length=50, default="fas fa-coins", verbose_name="Иконка")
    instructions = models.TextField(verbose_name="Инструкция", blank=True, 
                                   help_text="Что нужно сделать, чтобы получить награду")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Метод заработка"
        verbose_name_plural = "Методы заработка"
        ordering = ['-is_active', '-reward']
    
    def __str__(self):
        return f"{self.name} (+{self.reward} Аринкойнов)"

# Модель для заявок на заработок
class EarnRequest(models.Model):
    """Заявки на заработок Аринкойнов"""
    STATUS_CHOICES = [
        ('pending', '⏳ Ожидает проверки'),
        ('approved', '✅ Выполнено'),
        ('rejected', '❌ Отклонено'),
        ('cancelled', '🚫 Отменено'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    method = models.ForeignKey(EarnMethod, on_delete=models.CASCADE, verbose_name="Метод")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                             verbose_name="Статус")
    proof_text = models.TextField(verbose_name="Текст подтверждения", blank=True,
                                 help_text="Ссылка, скриншот или описание")
    admin_comment = models.TextField(verbose_name="Комментарий администратора", blank=True)
    coins_awarded = models.IntegerField(default=0, verbose_name="Начислено Аринкойнов")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='processed_earn_requests', verbose_name="Обработал")
    
    class Meta:
        verbose_name = "Заявка на заработок"
        verbose_name_plural = "Заявки на заработок"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.method.name} ({self.get_status_display()})"