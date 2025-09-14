#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
מחלקת בסיס לכל מנועי ה-Scraping
"""

import time
import logging
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from fake_useragent import UserAgent

from config import Config

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """מחלקת בסיס לכל מנועי ה-Scraping"""
    
    def __init__(self, store_name: str):
        self.store_name = store_name
        self.config = Config.get_store_config(store_name)
        
        if not self.config:
            raise ValueError(f"Store {store_name} not found in configuration")
        
        self.base_url = self.config['base_url']
        self.search_url = self.config['search_url']
        self.store_logo = self.config['logo']
        
        # הגדרות HTTP
        self.session = requests.Session()
        self.ua = UserAgent()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'he-IL,he;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # הגדרות Selenium
        self.selenium_options = Options()
        self.selenium_options.add_argument('--headless' if Config.SELENIUM_HEADLESS else '')
        self.selenium_options.add_argument('--no-sandbox')
        self.selenium_options.add_argument('--disable-dev-shm-usage')
        self.selenium_options.add_argument('--disable-gpu')
        self.selenium_options.add_argument(f'--user-agent={self.ua.random}')
        
    @abstractmethod
    def search_product(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        חיפוש מוצר בחנות
        
        Args:
            query: מחרוזת החיפוש
            max_results: מספר תוצאות מקסימלי
            
        Returns:
            רשימת מוצרים שנמצאו
        """
        pass
    
    def make_request(self, url: str, params: Dict = None) -> Optional[requests.Response]:
        """ביצוע בקשת HTTP עם retry ו-error handling"""
        for attempt in range(Config.MAX_RETRIES):
            try:
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=Config.REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Too Many Requests
                    logger.warning(f"Rate limited by {self.store_name}, waiting...")
                    time.sleep(Config.DELAY_BETWEEN_REQUESTS * 3)
                    continue
                else:
                    logger.warning(f"HTTP {response.status_code} from {self.store_name}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed for {self.store_name}: {e}")
                
            if attempt < Config.MAX_RETRIES - 1:
                time.sleep(Config.DELAY_BETWEEN_REQUESTS)
        
        return None
    
    def get_selenium_driver(self) -> webdriver.Chrome:
        """יצירת driver של Selenium"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.selenium_options)
            driver.set_page_load_timeout(Config.SELENIUM_TIMEOUT)
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create Selenium driver: {e}")
            raise
    
    def extract_price_from_text(self, text: str) -> Optional[float]:
        """חילוץ מחיר מטקסט עברי/אנגלי"""
        import re
        
        if not text:
            return None
        
        # ניקוי הטקסט
        text = text.replace(',', '').replace(' ', '')
        
        # דפוסים לחיפוש מחירים
        patterns = [
            r'₪([\d,\.]+)',  # ₪1,234.56
            r'([\d,\.]+)\s*₪',  # 1,234.56 ₪
            r'([\d,\.]+)\s*שקל',  # 1234 שקל
            r'([\d,\.]+)\s*ש"ח',  # 1234 ש"ח
            r'([\d,\.]+)'  # רק מספרים
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    price_str = match.group(1).replace(',', '')
                    price = float(price_str)
                    
                    # בדיקת סבירות המחיר
                    if 10 <= price <= 50000:  # מחירים סבירים לאלקטרוניקה
                        return price
                        
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def normalize_product_name(self, name: str) -> str:
        """נרמול שם מוצר"""
        if not name:
            return ""
        
        # ניקוי בסיסי
        name = name.strip()
        name = ' '.join(name.split())  # ניקוי רווחים כפולים
        
        # הסרת מילים מיותרות
        unwanted_words = ['בזוק', 'במבצע', 'הנחה', 'חדש', 'משלוח חינם']
        for word in unwanted_words:
            name = name.replace(word, '')
        
        return name.strip()
    
    def create_product_dict(self, name: str, price: float, url: str = None, 
                          image_url: str = None, availability: str = "זמין") -> Dict:
        """יצירת מילון מוצר סטנדרטי"""
        return {
            'name': self.normalize_product_name(name),
            'price': price,
            'store': self.config['name'],
            'store_logo': self.store_logo,
            'url': url,
            'image_url': image_url,
            'availability': availability,
            'last_updated': time.time()
        }
    
    def is_available(self) -> bool:
        """בדיקת זמינות החנות"""
        try:
            response = self.make_request(self.base_url)
            return response is not None and response.status_code == 200
        except Exception:
            return False
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.store_name})"
