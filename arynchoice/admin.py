from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import *

# Инлайн профиль в админке пользователей
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fields = ('arincoins', 'is_special_user')

# Кастомный админ для User
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'is_staff', 'get_arincoins')
    
    def get_arincoins(self, obj):
        return obj.userprofile.arincoins
    get_arincoins.short_description = 'Аринкойны'
    
    actions = ['add_50_coins', 'add_100_coins', 'reset_to_100']
    
    def add_50_coins(self, request, queryset):
        for user in queryset:
            profile = user.userprofile
            profile.arincoins += 50
            profile.save()
        self.message_user(request, f"✅ Начислено по 50 Аринкойнов {queryset.count()} пользователям")
    add_50_coins.short_description = "➕ Начислить 50 Аринкойнов"
    
    def add_100_coins(self, request, queryset):
        for user in queryset:
            profile = user.userprofile
            profile.arincoins += 100
            profile.save()
        self.message_user(request, f"✅ Начислено по 100 Аринкойнов {queryset.count()} пользователям")
    add_100_coins.short_description = "➕ Начислить 100 Аринкойнов"
    
    def reset_to_100(self, request, queryset):
        for user in queryset:
            profile = user.userprofile
            profile.arincoins = 100
            profile.save()
        self.message_user(request, f"🔄 Сброшено на 100 Аринкойнов {queryset.count()} пользователям")
    reset_to_100.short_description = "🔄 Сбросить на 100 Аринкойнов"

# Перерегистрируем User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Админка для профилей
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'arincoins', 'is_special_user')
    list_editable = ('arincoins',)
    search_fields = ('user__username', 'user__email')
    list_filter = ('is_special_user',)
    actions = ['add_50_coins_profile', 'add_100_coins_profile', 'set_500_coins']
    
    def add_50_coins_profile(self, request, queryset):
        for profile in queryset:
            profile.arincoins += 50
            profile.save()
        self.message_user(request, f"✅ Начислено по 50 Аринкойнов {queryset.count()} профилям")
    add_50_coins_profile.short_description = "➕ 50 Аринкойнов"
    
    def add_100_coins_profile(self, request, queryset):
        for profile in queryset:
            profile.arincoins += 100
            profile.save()
        self.message_user(request, f"✅ Начислено по 100 Аринкойнов {queryset.count()} профилям")
    add_100_coins_profile.short_description = "➕ 100 Аринкойнов"
    
    def set_500_coins(self, request, queryset):
        queryset.update(arincoins=500)
        self.message_user(request, f"🎁 Установлено 500 Аринкойнов {queryset.count()} профилям")
    set_500_coins.short_description = "🎁 Установить 500 Аринкойнов"

# Остальные модели
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'icon')
    search_fields = ('name',)
    ordering = ('order',)

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'duration', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_available')
    
    fieldsets = (
        ('Основное', {
            'fields': ('category', 'name', 'description', 'price', 'image')
        }),
        ('Детали', {
            'fields': ('duration', 'location', 'is_available')
        }),
    )

@admin.register(Selection)
class SelectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity', 'selected_at', 'is_confirmed')
    list_filter = ('is_confirmed', 'selected_at')
    search_fields = ('user__username', 'activity__name')


from .models import EarnMethod, EarnRequest

@admin.register(EarnMethod)
class EarnMethodAdmin(admin.ModelAdmin):
    """Админка для методов заработка"""
    list_display = ('name', 'reward', 'is_active', 'created_at')
    list_filter = ('is_active',)
    list_editable = ('reward', 'is_active')
    search_fields = ('name', 'description')
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'description', 'reward', 'icon')
        }),
        ('Инструкция', {
            'fields': ('instructions', 'is_active')
        }),
    )

@admin.register(EarnRequest)
class EarnRequestAdmin(admin.ModelAdmin):
    """Админка для заявок на заработок"""
    list_display = ('user', 'method', 'status', 'coins_awarded', 'created_at', 'get_status_emoji')
    list_filter = ('status', 'method', 'created_at')
    search_fields = ('user__username', 'proof_text', 'admin_comment')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_requests', 'reject_requests', 'award_50_coins']
    
    fieldsets = (
        ('Информация о заявке', {
            'fields': ('user', 'method', 'status', 'created_at')
        }),
        ('Подтверждение', {
            'fields': ('proof_text', 'admin_comment')
        }),
        ('Начисление', {
            'fields': ('coins_awarded', 'processed_by')
        }),
    )
    
    def get_status_emoji(self, obj):
        emojis = {
            'pending': '⏳',
            'approved': '✅',
            'rejected': '❌',
            'cancelled': '🚫'
        }
        return emojis.get(obj.status, '❓')
    get_status_emoji.short_description = ' '
    
    def approve_requests(self, request, queryset):
        """Одобрить заявки и начислить монеты"""
        for earn_request in queryset.filter(status='pending'):
            # Начисляем награду
            profile = earn_request.user.userprofile
            reward = earn_request.method.reward
            profile.arincoins += reward
            profile.save()
            
            # Обновляем заявку
            earn_request.status = 'approved'
            earn_request.coins_awarded = reward
            earn_request.processed_by = request.user
            earn_request.save()
            
        self.message_user(request, f"✅ Одобрено {queryset.count()} заявок, монеты начислены!")
    approve_requests.short_description = "✅ Одобрить и начислить награду"
    
    def reject_requests(self, request, queryset):
        """Отклонить заявки"""
        queryset.update(
            status='rejected',
            processed_by=request.user,
            admin_comment='Отклонено администратором'
        )
        self.message_user(request, f"❌ Отклонено {queryset.count()} заявок")
    reject_requests.short_description = "❌ Отклонить заявки"
    
    def award_50_coins(self, request, queryset):
        """Начислить 50 монет независимо от заявки"""
        for earn_request in queryset:
            profile = earn_request.user.userprofile
            profile.arincoins += 50
            profile.save()
            
            earn_request.coins_awarded += 50
            earn_request.admin_comment += f"\nДополнительно начислено 50 монет администратором {request.user}"
            earn_request.save()
            
        self.message_user(request, f"💰 Начислено по 50 монет {queryset.count()} пользователям")
    award_50_coins.short_description = "💰 Начислить дополнительные 50 монет"