# arynchoice/management/commands/load_collections.py
import requests
from django.core.management.base import BaseCommand
from arynchoice.models import Category, Activity
import time

class Command(BaseCommand):
    help = 'Загружает подборки фильмов, сериалов и аниме'
    
    def handle(self, *args, **kwargs):
        
        TOKEN = "RH4ZBVW-ZTB41ZH-QCTGSTJ-FXZGMXQ"  
        
        
        headers = {"X-API-KEY": TOKEN}
        
        # ===========================================
        # 2. СОЗДАЕМ КАТЕГОРИИ (4 штуки)
        # ===========================================
        
        categories = [
            {
                'name': '🎬 Лучшие фильмы для двоих',
                'description': 'Романтика, драма, приключения - идеально для уютного вечера',
                'icon': 'fas fa-film',
                'order': 1,
                'api_params': {
                    'rating.kp': '6-10',
                    'year': '2000-2024',
                    'genres': ['драма', 'мелодрама', 'комедия'],
                    'sortField': 'rating.kp',
                    'sortType': -1,
                    'limit': 15
                }
            },
            {
                'name': '📺 Лучшие сериалы',
                'description': 'Захватывающие истории на несколько вечеров',
                'icon': 'fas fa-tv',
                'order': 2,
                'api_params': {
                    'rating.kp': '6-10',
                    'year': '2000-2024',
                    'type': 'tv-series',
                    'sortField': 'rating.kp',
                    'sortType': -1,
                    'limit': 20
                }
            },
            {
                'name': '🇯🇵 Лучшее аниме',
                'description': 'Японская анимация для души',
                'icon': 'fas fa-dragon',
                'order': 3,
                'api_params': {
                    'rating.kp': '1-10',
                    'genres': ['аниме'],
                    'sortField': 'rating.kp',
                    'sortType': -1,
                    'limit': 20
                }
            },
            {
                'name': '🍿 Комедии для настроения',
                'description': 'Посмеяться от души',
                'icon': 'fas fa-laugh',
                'order': 4,
                'api_params': {
                    'rating.kp': '5-9',
                    'genres': ['комедия'],
                    'sortField': 'rating.kp',
                    'sortType': -1,
                    'limit': 20
                }
            }
        ]
        
        # ===========================================
        # 3. ЗАГРУЖАЕМ ФИЛЬМЫ ДЛЯ КАЖДОЙ КАТЕГОРИИ
        # ===========================================
        
        total_added = 0
        
        for cat_data in categories:
            # Создаем или получаем категорию
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'order': cat_data['order']
                }
            )
            
            if created:
                self.stdout.write(f'✅ Создана категория: {cat_data["name"]}')
            else:
                self.stdout.write(f'⏭️  Категория уже есть: {cat_data["name"]}')
            
            # Загружаем фильмы с API
            self.stdout.write(f'   Загружаем фильмы...')
            
            url = "https://api.kinopoisk.dev/v1.4/movie"
            
            try:
                response = requests.get(url, headers=headers, params=cat_data['api_params'], timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    movies = data.get('docs', [])
                    
                    added = 0
                    for movie in movies:
                        # Получаем название
                        name = movie.get('name')
                        alt_name = movie.get('alternativeName')
                        
                        if not name:
                            name = alt_name
                        if not name:
                            continue
                        
                        # Получаем описание
                        description = movie.get('shortDescription') or movie.get('description') or 'Нет описания'
                        description = description[:300]  # Обрезаем
                        
                        # Получаем рейтинг
                        rating = movie.get('rating', {}).get('kp', 0)
                        rating_display = f"{rating:.1f}" if rating else "?"
                        
                        # Получаем год
                        year = movie.get('year', '')
                        
                        # Получаем длительность
                        duration = movie.get('movieLength')
                        if not duration:
                            duration = movie.get('seriesLength', '?')
                        
                        # Цена зависит от рейтинга
                        price = 3
                        
                        
                        # Формируем полное описание
                        full_description = f"⭐ Рейтинг: {rating_display}\n📅 Год: {year}\n\n{description}"
                        
                        # Создаем фильм
                        activity, created = Activity.objects.get_or_create(
                            name=name,
                            defaults={
                                'category': category,
                                'description': full_description,
                                'price': price,
                                'duration': f"{duration} мин" if duration else "2 часа",
                                'location': 'Дома',
                                'is_available': True
                            }
                        )
                        
                        if created:
                            added += 1
                            total_added += 1
                    
                    self.stdout.write(self.style.SUCCESS(f'   ✅ Добавлено {added} фильмов в "{cat_data["name"]}"'))
                    
                    # Если ничего не добавилось
                    if added == 0:
                        self.stdout.write(self.style.WARNING(f'   ⚠️  Нет новых фильмов в этой категории'))
                        
                else:
                    self.stdout.write(self.style.ERROR(f'   ❌ Ошибка API: {response.status_code}'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Ошибка загрузки: {e}'))
            
            # Ждем секунду между запросами (чтобы не заблокировали)
            time.sleep(1)
        
        # ===========================================
        # 4. ИТОГИ
        # ===========================================
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'🎉 ГОТОВО! Добавлено {total_added} фильмов/сериалов/аниме'))
        self.stdout.write('='*50)
        self.stdout.write('\n📊 Статистика:')
        
        for category in Category.objects.all():
            count = Activity.objects.filter(category=category).count()
            self.stdout.write(f'   {category.name}: {count} позиций')
        
        self.stdout.write('\n🌐 Запусти сервер: python manage.py runserver')
        self.stdout.write('📱 Открой сайт и смотри результат!\n')