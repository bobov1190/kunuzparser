"""
KunUz Parser - Удобный парсер новостей
Простое использование: kunuzparser() или kunuzparser('health', limit=10)
"""

import re
from typing import List, Dict, Optional, Union
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from pathlib import Path
import json

from config import CATEGORIES, BASE_URL, OUTPUT_DIR


FOOTER_RE = re.compile(
    r'"?KUN\.UZ"? saytida eʼlon qilingan materiallardan.*$',
    re.DOTALL | re.IGNORECASE
)


class KunUzParser:
    """Парсер новостей с Kun.uz"""
    
    def __init__(self):
        self.output_dir = Path(OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)

    def clean_content(self, text: str) -> str:
        """Очистка контента от футеров и лишних элементов"""
        text = re.sub(FOOTER_RE, "", text or "")
        text = re.sub(
            r'\b(Foto|Фото|Surat|Rasm)\s*:\s*[^.]+\.*',
            '',
            text,
            flags=re.IGNORECASE
        )
        return re.sub(r"\s+", " ", text).strip()

    def extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Извлечение даты публикации"""
        meta = soup.select_one('meta[property="article:published_time"]')
        if meta and meta.get("content"):
            try:
                return datetime.fromisoformat(meta["content"].replace("Z", ""))
            except Exception:
                pass

        m = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', soup.get_text())
        if m:
            return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        return None

    def date_allowed(
        self, 
        date: Optional[datetime], 
        from_date: Optional[datetime], 
        to_date: Optional[datetime]
    ) -> bool:
        """Проверка попадания даты в диапазон"""
        if not date:
            return True
        if from_date and date < from_date:
            return False
        if to_date and date > to_date:
            return False
        return True

    def scroll_until_button(self, page) -> bool:
        """Прокрутка страницы до кнопки загрузки"""
        for _ in range(6):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1200)
            if page.query_selector("div.point-view__footer button"):
                return True
        return False

    def fetch_list(self, page, url: str, limit: int) -> List[str]:
        """Сбор списка URL новостей"""
        page.goto(url, wait_until="networkidle")
        collected = set()

        while len(collected) < limit:
            soup = BeautifulSoup(page.content(), "lxml")

            for a in soup.select("a.news-page__item[href]"):
                href = a.get("href")
                if href and re.search(r"/news/\d{4}/\d{2}/\d{2}/", href):
                    collected.add(BASE_URL + href)
                    if len(collected) >= limit:
                        break

            if len(collected) >= limit:
                break

            if not self.scroll_until_button(page):
                break

            page.click("div.point-view__footer button")
            page.wait_for_timeout(1800)

        return list(collected)[:limit]

    def fetch_detail(
        self, 
        page, 
        url: str, 
        category: str,
        from_date: Optional[datetime],
        to_date: Optional[datetime]
    ) -> Optional[Dict]:
        """Парсинг детальной страницы новости"""
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
        except Exception:
            return None
            
        soup = BeautifulSoup(page.content(), "lxml")

        h1 = soup.find("h1")
        if not h1:
            return None

        published_at = self.extract_date(soup)
        if not self.date_allowed(published_at, from_date, to_date):
            return None

        block = (
            soup.select_one("div.single-content")
            or soup.select_one("div.news-inner__content")
        )
        if not block:
            return None

        for tag in block.select("script, style, figure, iframe, .share, .ads"):
            tag.decompose()

        text = " ".join(
            p.get_text(" ", strip=True)
            for p in block.find_all("p")
            if "cookies" not in p.get_text(strip=True).lower()
        )

        content = self.clean_content(text)
        if len(content) < 200:
            return None

        img = soup.select_one('meta[property="og:image"]')

        return {
            "title": h1.get_text(strip=True),
            "content": content,
            "image_url": img["content"] if img else None,
            "published_at": published_at.isoformat() if published_at else None,
            "source_url": url,
            "source": "kunuz",
            "category": category,
            "language": "uz"
        }

    def parse_category(
        self,
        page,
        key: str,
        limit: int,
        from_date: Optional[datetime],
        to_date: Optional[datetime],
        verbose: bool = True
    ) -> List[Dict]:
        """Парсинг одной категории"""
        cfg = CATEGORIES.get(key)
        if not cfg:
            if verbose:
                print(f"❌ Категория '{key}' не найдена")
            return []

        if verbose:
            print(f"🚀 Парсинг: {key} (лимит: {limit})")
        
        urls = self.fetch_list(page, cfg["url"], limit)
        if verbose:
            print(f"   Найдено URL: {len(urls)}")

        results = []
        for i, url in enumerate(urls, 1):
            item = self.fetch_detail(page, url, cfg["category_name"], from_date, to_date)
            if item:
                results.append(item)
                if verbose:
                    print(f"   ✓ [{i}/{len(urls)}] {item['title'][:50]}...")
            else:
                if verbose:
                    print(f"   ✗ [{i}/{len(urls)}] Пропущено")

        return results

    def parse(
        self,
        category: Union[str, List[str]] = 'everything',
        limit: int = 20,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        save: bool = True,
        verbose: bool = True
    ) -> List[Dict]:
        """
        Главная функция парсинга
        
        Args:
            category: Категория или список категорий ('health', 'world', 'everything')
            limit: Количество новостей (default: 20)
            from_date: Дата начала 'YYYY-MM-DD'
            to_date: Дата окончания 'YYYY-MM-DD'
            save: Сохранять ли в JSON файл
            verbose: Выводить ли прогресс
            
        Returns:
            Список новостей (list of dict)
        """
        
        # Парсинг дат
        fd = datetime.strptime(from_date, "%Y-%m-%d") if from_date else None
        td = datetime.strptime(to_date, "%Y-%m-%d") if to_date else None

        all_results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Everything - собираем со всех категорий
            if category == 'everything':
                if verbose:
                    print(f"\n🌟 РЕЖИМ: EVERYTHING (всего {limit} новостей)")
                
                categories_list = list(CATEGORIES.keys())
                per_category = max(1, limit // len(categories_list))
                remainder = limit % len(categories_list)
                
                for i, key in enumerate(categories_list):
                    cat_limit = per_category + (1 if i < remainder else 0)
                    results = self.parse_category(page, key, cat_limit, fd, td, verbose)
                    all_results.extend(results)
                    
                    if len(all_results) >= limit:
                        all_results = all_results[:limit]
                        break
            
            # Одна или несколько категорий
            else:
                cats = [category] if isinstance(category, str) else category
                
                for key in cats:
                    results = self.parse_category(page, key, limit, fd, td, verbose)
                    all_results.extend(results)

            page.close()
            browser.close()

        # Сохранение
        if save and all_results:
            filename = f"kunuz_{category if isinstance(category, str) else 'multiple'}.json"
            path = self.output_dir / filename
            
            with open(path, "w", encoding="utf-8") as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
            
            if verbose:
                print(f"\n💾 Сохранено: {len(all_results)} новостей → {path}")

        if verbose:
            print(f"\n✅ Готово! Всего новостей: {len(all_results)}")
        
        return all_results


def kunuzparser(
    category: Union[str, List[str]] = 'everything',
    limit: int = 20,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    save: bool = True,
    verbose: bool = True
) -> List[Dict]:
    """
    Удобная функция для парсинга новостей с Kun.uz
    
    Примеры:
        # Все категории (20 новостей)
        kunuzparser()
        
        # Здоровье (10 новостей)
        kunuzparser('health', limit=10)
        
        # Несколько категорий
        kunuzparser(['health', 'sport'], limit=30)
        
        # С фильтром по дате
        kunuzparser('world', from_date='2026-01-25')
    
    Категории:
        - health (здоровье)
        - world (мировые новости)
        - economy (экономика)
        - sport (спорт)
        - technology (технологии)
        - education (образование)
        - useful (туризм/развлечения)
        - everything (все категории)
    
    Args:
        category: Категория или список категорий
        limit: Количество новостей
        from_date: Дата начала 'YYYY-MM-DD'
        to_date: Дата окончания 'YYYY-MM-DD'
        save: Сохранять результаты в JSON
        verbose: Показывать прогресс
        
    Returns:
        Список новостей (list of dict)
    """
    parser = KunUzParser()
    return parser.parse(category, limit, from_date, to_date, save, verbose)
