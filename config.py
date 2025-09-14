#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
הגדרות מערכת PriceHunter
"""

import os

class Config:
    """הגדרות כלליות של המערכת"""
    
    # הגדרות בסיסיות
    PROJECT_NAME = "PriceHunter"
    VERSION = "1.0.0"
    DEBUG = True
    
    # הגדרות Scraping
    REQUEST_TIMEOUT = 10  # שניות
    MAX_RETRIES = 3
    DELAY_BETWEEN_REQUESTS = 1  # שניה
    
    # User Agent לבקשות HTTP
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
    ]
    
    # הגדרות מטמון
    CACHE_DURATION = 300  # 5 דקות
    ENABLE_CACHE = True
    
    # חנויות פעילות
    ACTIVE_STORES = {
        'ksp': {
            'name': 'KSP',
            'base_url': 'https://ksp.co.il',
            'search_url': 'https://ksp.co.il/web/cat/573..2',
            'logo': 'K',
            'enabled': True
        },
        'bug': {
            'name': 'Bug',
            'base_url': 'https://www.bug.co.il',
            'search_url': 'https://www.bug.co.il/search',
            'logo': 'B', 
            'enabled': True
        },
        'zap': {
            'name': 'זאפ',
            'base_url': 'https://www.zap.co.il',
            'search_url': 'https://www.zap.co.il/search.aspx',
            'logo': 'Z',
            'enabled': True
        },
        'ivory': {
            'name': 'Ivory',
            'base_url': 'https://www.ivory.co.il',
            'search_url': 'https://www.ivory.co.il/catalog.php',
            'logo': 'I',
            'enabled': True
        }
    }
    
    # קטגוריות מוצרים
    ELECTRONICS_CATEGORIES = [
        'smartphones',
        'laptops', 
        'tablets',
        'headphones',
        'smartwatches',
        'cameras',
        'gaming',
        'tv',
        'audio'
    ]
    
    # הגדרות מסד נתונים
    DATABASE_PATH = 'cache.db'
    
    # הגדרות Flask
    FLASK_HOST = '127.0.0.1'
    FLASK_PORT = 5000
    FLASK_DEBUG = DEBUG
    
    # הגדרות Selenium
    SELENIUM_HEADLESS = True
    SELENIUM_TIMEOUT = 15
    
    @staticmethod
    def get_store_config(store_name):
        """קבלת הגדרות חנות ספציפית"""
        return Config.ACTIVE_STORES.get(store_name.lower())
    
    @staticmethod
    def is_store_enabled(store_name):
        """בדיקה אם חנות פעילה"""
        store_config = Config.get_store_config(store_name)
        return store_config and store_config.get('enabled', False)