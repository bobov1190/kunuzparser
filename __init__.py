"""
KunUz Parser - Простой парсер новостей с Kun.uz
Автор: Claude
Версия: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Claude"

from .parser import kunuzparser
from .config import CATEGORIES

__all__ = ['kunuzparser', 'CATEGORIES']
