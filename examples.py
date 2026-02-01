"""
Примеры использования KunUz Parser
"""

from kunuzparser import kunuzparser


def example_1_basic():
    """Базовый пример: все новости"""
    print("=" * 60)
    print("Пример 1: Все категории (20 новостей)")
    print("=" * 60)
    
    news = kunuzparser()
    
    print(f"\nПолучено новостей: {len(news)}")
    if news:
        print(f"\nПервая новость:")
        print(f"  Заголовок: {news[0]['title']}")
        print(f"  Категория: {news[0]['category']}")
        print(f"  Дата: {news[0]['published_at']}")


def example_2_category():
    """Пример: конкретная категория"""
    print("\n" + "=" * 60)
    print("Пример 2: Новости о здоровье (10 штук)")
    print("=" * 60)
    
    news = kunuzparser('health', limit=10)
    
    for i, article in enumerate(news, 1):
        print(f"\n[{i}] {article['title']}")
        print(f"    {article['content'][:100]}...")


def example_3_multiple():
    """Пример: несколько категорий"""
    print("\n" + "=" * 60)
    print("Пример 3: Спорт + Технологии (20 новостей)")
    print("=" * 60)
    
    news = kunuzparser(['sport', 'technology'], limit=20)
    
    print(f"\nПолучено новостей: {len(news)}")
    
    # Группировка по категориям
    by_category = {}
    for article in news:
        cat = article['category']
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print("\nРаспределение по категориям:")
    for cat, count in by_category.items():
        print(f"  {cat}: {count}")


def example_4_dates():
    """Пример: фильтр по датам"""
    print("\n" + "=" * 60)
    print("Пример 4: Свежие новости с 25 января")
    print("=" * 60)
    
    news = kunuzparser('world', from_date='2026-01-25', limit=15)
    
    print(f"\nПолучено новостей: {len(news)}")
    if news:
        print(f"Самая свежая: {news[0]['title']}")


def example_5_no_save():
    """Пример: без сохранения"""
    print("\n" + "=" * 60)
    print("Пример 5: Без сохранения в файл")
    print("=" * 60)
    
    news = kunuzparser('economy', limit=5, save=False, verbose=False)
    
    print(f"Получено новостей: {len(news)}")
    for article in news:
        print(f"  • {article['title'][:60]}...")


def example_6_export_csv():
    """Пример: экспорт в CSV"""
    print("\n" + "=" * 60)
    print("Пример 6: Экспорт в CSV")
    print("=" * 60)
    
    import csv
    
    news = kunuzparser('technology', limit=10, verbose=False)
    
    with open('parsed_data/news.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'category', 'published_at', 'source_url'])
        writer.writeheader()
        writer.writerows(news)
    
    print("✅ Экспортировано в parsed_data/news.csv")


if __name__ == "__main__":
    # Запуск всех примеров
    example_1_basic()
    # example_2_category()
    # example_3_multiple()
    # example_4_dates()
    # example_5_no_save()
    # example_6_export_csv()
    
    print("\n" + "=" * 60)
    print("✅ Примеры завершены!")
    print("=" * 60)
