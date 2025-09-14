#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
המנוע הראשי לחיפוש וההשוואת מחירים
"""

import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from datetime import datetime

from config import Config
from scrapers.ksp_scraper import KSPScraper
from scrapers.bug_scraper import BugScraper  # נבנה בהמשך
from scrapers.zap_scraper import ZapScraper  # נבנה בהמשך
from scrapers.ivory_scraper import IvoryScraper  # נבנה בהמשך

logger = logging.getLogger(__name__)

class PriceFinder:
    """המנוע הראשי לחיפוש והשוואת מחירים"""
    
    def __init__(self):
        self.scrapers = {}
        self._initialize_scrapers()
        
    def _initialize_scrapers(self):
        """אתחול כל מנועי ה-Scraping"""
        scraper_classes = {
            'ksp': KSPScraper,
            # 'bug': BugScraper,      # נוסיף בהמשך
            # 'zap': ZapScraper,      # נוסיף בהמשך  
            # 'ivory': IvoryScraper   # נוסיף בהמשך
        }
        
        for store_name, scraper_class in scraper_classes.items():
            if Config.is_store_enabled(store_name):
                try:
                    self.scrapers[store_name] = scraper_class()
                    logger.info(f"Initialized {store_name} scraper")
                except Exception as e:
                    logger.error(f"Failed to initialize {store_name} scraper: {e}")
    
    def search_all_stores(self, query: str, max_results_per_store: int = 5) -> Dict:
        """
        חיפוש מוצר בכל החנויות
        
        Args:
            query: מחרוזת החיפוש
            max_results_per_store: מספר תוצאות מקסימלי לכל חנות
            
        Returns:
            Dictionary עם תוצאות החיפוש
        """
        logger.info(f"Starting search for: '{query}'")
        start_time = time.time()
        
        results = {
            'query': query,
            'search_time': None,
            'stores_searched': [],
            'total_products': 0,
            'products': [],
            'best_deal': None,
            'errors': []
        }
        
        # ביצוע חיפוש במקביל
        with ThreadPoolExecutor(max_workers=len(self.scrapers)) as executor:
            future_to_store = {
                executor.submit(self._search_single_store, store_name, scraper, query, max_results_per_store): store_name
                for store_name, scraper in self.scrapers.items()
            }
            
            for future in as_completed(future_to_store):
                store_name = future_to_store[future]
                results['stores_searched'].append(store_name)
                
                try:
                    store_products = future.result(timeout=30)  # מקסימום 30 שניות לכל חנות
                    
                    if store_products:
                        results['products'].extend(store_products)
                        logger.info(f"Found {len(store_products)} products in {store_name}")
                    else:
                        logger.warning(f"No products found in {store_name}")
                        
                except Exception as e:
                    error_msg = f"Error searching {store_name}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
        
        # סיכום התוצאות
        results['total_products'] = len(results['products'])
        results['search_time'] = round(time.time() - start_time, 2)
        
        # מציאת העסקה הטובה ביותר
        if results['products']:
            results['best_deal'] = self._find_best_deal(results['products'])
            results['products'] = self._sort_products_by_price(results['products'])
        
        logger.info(f"Search completed: {results['total_products']} products in {results['search_time']}s")
        return results
    
    def _search_single_store(self, store_name: str, scraper, query: str, max_results: int) -> List[Dict]:
        """חיפוש בחנות בודדת"""
        try:
            logger.debug(f"Searching {store_name} for '{query}'")
            products = scraper.search_product(query, max_results)
            return products or []
        except Exception as e:
            logger.error(f"Failed to search {store_name}: {e}")
            return []
    
    def _find_best_deal(self, products: List[Dict]) -> Optional[Dict]:
        """מציאת העסקה הטובה ביותר"""
        if not products:
            return None
        
        # מיון לפי מחיר (הכי זול קודם)
        sorted_products = sorted(products, key=lambda p: p.get('price', float('inf')))
        best_product = sorted_products[0]
        
        # הוספת מידע על החיסכון
        if len(sorted_products) > 1:
            most_expensive = sorted_products[-1]
            savings = most_expensive['price'] - best_product['price']
            best_product['savings'] = savings
            best_product['savings_percent'] = round((savings / most_expensive['price']) * 100, 1)
        
        return best_product
    
    def _sort_products_by_price(self, products: List[Dict]) -> List[Dict]:
        """מיון מוצרים לפי מחיר"""
        return sorted(products, key=lambda p: p.get('price', float('inf')))
    
    def get_store_status(self) -> Dict:
        """קבלת סטטוס כל החנויות"""
        status = {}
        
        for store_name, scraper in self.scrapers.items():
            try:
                is_available = scraper.is_available()
                status[store_name] = {
                    'name': scraper.config['name'],
                    'available': is_available,
                    'url': scraper.base_url
                }
            except Exception as e:
                status[store_name] = {
                    'name': store_name,
                    'available': False,
                    'error': str(e)
                }
        
        return status
    
    def search_specific_stores(self, query: str, store_names: List[str], max_results: int = 5) -> Dict:
        """חיפוש בחנויות ספציפיות בלבד"""
        # סינון החנויות המבוקשות
        filtered_scrapers = {
            name: scraper for name, scraper in self.scrapers.items() 
            if name in store_names
        }
        
        if not filtered_scrapers:
            return {
                'query': query,
                'error': 'None of the requested stores are available',
                'products': []
            }
        
        # שמירה זמנית של הscrpers המקוריים
        original_scrapers = self.scrapers
        self.scrapers = filtered_scrapers
        
        try:
            # ביצוע החיפוש
            results = self.search_all_stores(query, max_results)
            return results
        finally:
            # החזרת הscrpers המקוריים
            self.scrapers = original_scrapers
