#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrapers Package
חבילת מנועי חילוץ נתונים מהחנויות

תיקייה זו מכילה:
- base_scraper.py: המחלקה הבסיסית לכל הscrapers
- ksp_scraper.py: מנוע חילוץ מ-KSP
- bug_scraper.py: מנוע חילוץ מ-Bug (עתיד)
- zap_scraper.py: מנוע חילוץ מ-זאפ (עתיד)
- ivory_scraper.py: מנוע חילוץ מ-Ivory (עתיד)

איך זה עובד:
1. כל חנות = קובץ נפרד
2. כל scraper יורש מ-BaseScraper
3. המערכת טוענת את כולם אוטומטית
4. קל להוסיף חנות חדשה - רק קובץ אחד!
"""

# imports - מה מהתיקייה הזו אפשר להשתמש בו מבחוץ
from .base_scraper import BaseScraper

# ייבוא scrapers נוספים כשהם יהיו מוכנים
try:
    from .ksp_scraper import KSPScraper
except ImportError:
    # אם עוד לא קיים הקובץ - לא נורא
    KSPScraper = None

try:
    from .bug_scraper import BugScraper
except ImportError:
    BugScraper = None

try:
    from .zap_scraper import ZapScraper  
except ImportError:
    ZapScraper = None

try:
    from .ivory_scraper import IvoryScraper
except ImportError:
    IvoryScraper = None

# רשימת כל מה שאפשר להשתמש בו מהחבילה הזו
__all__ = [
    'BaseScraper',      # המחלקה הבסיסית
    'KSPScraper',       # KSP (יהיה בשלב הבא)
    'BugScraper',       # Bug (עתיד)
    'ZapScraper',       # זאפ (עתיד)
    'IvoryScraper'      # Ivory (עתיד)
]
