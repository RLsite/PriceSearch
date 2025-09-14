#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Package - המוח של PriceHunter
תיקיית הלוגיקה המרכזית

מה יש כאן:
1. price_finder.py - המנוע הראשי שמחבר כל הscrapers
2. product_matcher.py - זיהוי מוצרים זהים בחנויות שונות (עתיד)
3. data_cleaner.py - ניקוי וארגון נתונים (עתיד)

איך זה עובד:
- Scrapers אוספים נתונים גולמיים מהחנויות
- Core מעבד, מנתח ומחזיר תוצאות מסודרות
- המשתמש מקבל השוואת מחירים מושלמת

זה כמו מפעל:
- Scrapers = פועלים שאוספים חומרים
- Core = המכונות שמעבדות
- User = מקבל מוצר מוגמר
"""

# ייבוא המחלקות הראשיות כשהן יהיו מוכנות
try:
    from .price_finder import PriceFinder
except ImportError:
    # עוד לא קיים - נוסיף בשלב הבא
    PriceFinder = None

try:
    from .product_matcher import ProductMatcher
except ImportError:
    # עתיד
    ProductMatcher = None

try:
    from .data_cleaner import DataCleaner
except ImportError:
    # עתיד  
    DataCleaner = None

# מה ציבורי בחבילה זו
__all__ = [
    'PriceFinder',      # המנוע הראשי (שלב הבא)
    'ProductMatcher',   # זיהוי מוצרים זהים (עתיד)
    'DataCleaner'       # ניקוי נתונים (עתיד)
]

# מידע על החבילה
__version__ = '1.0.0'
__author__ = 'PriceHunter Team'
__description__ = 'המוח של מערכת השוואת המחירים'
