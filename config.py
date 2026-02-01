# config.py

CATEGORIES = {
    'health': {
        'url': 'https://kun.uz/news/category/soglom-hayot',
        'category_name': 'health',
        'limit': 20,
        'from_date': None,
        'to_date': None
    },
    'world': {
        'url': 'https://kun.uz/news/category/jahon',
        'category_name': 'global',
        'limit': 20,
        'from_date': None,
        'to_date': None
    },
    'economy': {
        'url': 'https://kun.uz/news/category/iqtisodiyot',
        'category_name': 'business',
        'limit': 20,
        'from_date': None,
        'to_date': None
    },
    'sport': {
        'url': 'https://kun.uz/news/category/sport',
        'category_name': 'sports',
        'limit': 20,
        'from_date': None,
        'to_date': None
    },
    'technology': {
        'url': 'https://kun.uz/news/category/texnologiya',
        'category_name': 'technology',
        'limit': 20,
        'from_date': None,
        'to_date': None
    },
    'education': {
        'url': 'https://kun.uz/news/category/talim',
        'category_name': 'science',
        'limit': 20,
        'from_date': None,
        'to_date': None
    },
    'useful': {
        'url': 'https://kun.uz/news/category/turizm',
        'category_name': 'entertainment',
        'limit': 20,
        'from_date': None,
        'to_date': None
    }
}

BASE_URL = "https://kun.uz"
OUTPUT_DIR = "parsed_data"
