# KunUz Parser 🚀

Простой и удобный парсер новостей с сайта Kun.uz

## Установка

```bash
pip install -r requirements.txt
playwright install chromium
```

## Использование

### Быстрый старт

```python
from kunuzparser import kunuzparser

# Все категории, 20 новостей
news = kunuzparser()

# Конкретная категория
news = kunuzparser('health', limit=10)

# Несколько категорий
news = kunuzparser(['health', 'sport'], limit=30)

# С фильтром по дате
news = kunuzparser('world', from_date='2026-01-25')
```

### Примеры

```python
# Пример 1: Получить 20 новостей о здоровье
news = kunuzparser('health')
for article in news:
    print(article['title'])
    print(article['content'][:100])
    print('---')

# Пример 2: Все категории
news = kunuzparser('everything', limit=50)
print(f"Получено {len(news)} новостей")

# Пример 3: Свежие новости за последнюю неделю
from datetime import datetime, timedelta

week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
news = kunuzparser('world', from_date=week_ago, limit=30)

# Пример 4: Без сохранения в файл
news = kunuzparser('sport', limit=15, save=False)

# Пример 5: Тихий режим (без вывода прогресса)
news = kunuzparser('technology', verbose=False)
```

## Доступные категории

- `health` - Здоровье
- `world` - Мировые новости
- `economy` - Экономика
- `sport` - Спорт
- `technology` - Технологии
- `education` - Образование
- `useful` - Туризм и развлечения
- `everything` - Все категории сразу

## Параметры функции

```python
kunuzparser(
    category='everything',    # Категория или список категорий
    limit=20,                # Количество новостей
    from_date=None,          # Дата начала 'YYYY-MM-DD'
    to_date=None,            # Дата окончания 'YYYY-MM-DD'
    save=True,               # Сохранять в JSON файл
    verbose=True             # Показывать прогресс
)
```

## Формат данных

Каждая новость возвращается в виде словаря:

```python
{
    "title": "Заголовок новости",
    "content": "Полный текст новости...",
    "image_url": "https://...",
    "published_at": "2026-01-31T12:00:00",
    "source_url": "https://kun.uz/news/...",
    "source": "kunuz",
    "category": "health",
    "language": "uz"
}
```

## Сохранение результатов

По умолчанию результаты сохраняются в папку `parsed_data/` в формате JSON:

- `kunuz_health.json` - для одной категории
- `kunuz_everything.json` - для всех категорий
- `kunuz_multiple.json` - для нескольких категорий

## Использование как модуль

```python
# Импорт
from kunuzparser import kunuzparser, CATEGORIES

# Просмотр доступных категорий
print(CATEGORIES.keys())

# Парсинг
news = kunuzparser('health', limit=10)

# Обработка результатов
for article in news:
    print(f"{article['title']}")
    print(f"Опубликовано: {article['published_at']}")
```

## CLI использование

```python
# examples.py
from kunuzparser import kunuzparser

if __name__ == "__main__":
    import sys
    
    category = sys.argv[1] if len(sys.argv) > 1 else 'everything'
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    print(f"Парсинг: {category}, лимит: {limit}")
    news = kunuzparser(category, limit=limit)
    print(f"Получено: {len(news)} новостей")
```

Запуск:
```bash
python examples.py health 10
```

## Требования

- Python 3.8+
- BeautifulSoup4
- lxml  
- Playwright

## Лицензия

MIT

## Автор

Создано с помощью Claude AI
