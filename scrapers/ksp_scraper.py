#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KSP Scraper - חילוץ מחירים מאתר KSP
"""

import time
import logging
from typing import List, Dict
from urllib.parse import urljoin, quote
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class KSPScraper(BaseScraper):
    """Scraper עבור אתר KSP - ksp.co.il"""
    
    def __init__(self):
        super().__init__('ksp')
    
    def search_product(self, query: str, max_results: int = 10) -> List[Dict]:
        """חיפוש מוצר באתר KSP"""
        logger.info(f"Searching KSP for: {query}")
        
        try:
            return self._search_with_selenium(query, max_results)
        except Exception as e:
            logger.error(f"KSP search failed for '{query}': {e}")
            return []
    
    def _search_with_selenium(self, query: str, max_results: int) -> List[Dict]:
        """ביצוע חיפוש עם Selenium"""
        driver = None
        products = []
        
        try:
            driver = self.get_selenium_driver()
            
            # מעבר לעמוד הראשי
            driver.get(self.base_url)
            logger.debug("Loaded KSP homepage")
            
            # המתנה לטעינת הדף
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # חיפוש תיבת החיפוש
            search_selectors = [
                'input[name="keyword"]',
                'input[placeholder*="חיפוש"]',
                '#search-input',
                '.search-input',
                'input[type="search"]'
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not search_box:
                logger.error("Could not find search box on KSP")
                return []
            
            # הכנסת טקסט החיפוש
            search_box.clear()
            search_box.send_keys(query)
            
            # לחיצה על כפתור החיפוש
            search_button_selectors = [
                'button[type="submit"]',
                '.search-btn',
                '#search-btn',
                'input[type="submit"]'
            ]
            
            search_button = None
            for selector in search_button_selectors:
                try:
                    search_button = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if search_button:
                search_button.click()
            else:
                # אם אין כפתור, נסה Enter
                from selenium.webdriver.common.keys import Keys
                search_box.send_keys(Keys.RETURN)
            
            # המתנה לתוצאות
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        '.product-item, .item, .product, .result-item'
                    ))
                )
            except TimeoutException:
                logger.warning("No products found on KSP results page")
                return []
            
            time.sleep(2)  # המתנה נוספת לטעינה מלאה
            
            # חילוץ מוצרים
            product_selectors = [
                '.product-item',
                '.item',
                '.product',
                '.result-item',
                '[data-product]'
            ]
            
            product_elements = []
            for selector in product_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    product_elements = elements[:max_results]
                    break
            
            logger.info(f"Found {len(product_elements)} products on KSP")
            
            for element in product_elements:
                product_data = self._extract_product_data(element)
                if product_data:
                    products.append(product_data)
            
            return products
            
        except Exception as e:
            logger.error(f"Selenium search failed on KSP: {e}")
            return []
        
        finally:
            if driver:
                driver.quit()
    
    def _extract_product_data(self, element) -> Dict:
        """חילוץ נתוני מוצר מאלמנט HTML"""
        try:
            # שם המוצר
            name_selectors = [
                '.product-title',
                '.item-name', 
                'h3',
                'h4',
                '.name',
                '.title',
                'a[title]'
            ]
            
            product_name = None
            for selector in name_selectors:
                try:
                    name_element = element.find_element(By.CSS_SELECTOR, selector)
                    product_name = name_element.text.strip() or name_element.get_attribute('title')
                    if product_name:
                        break
                except NoSuchElementException:
                    continue
            
            if not product_name:
                logger.debug("Could not extract product name from KSP element")
                return None
            
            # מחיר
            price_selectors = [
                '.price',
                '.current-price',
                '.item-price',
                '.cost',
                '.price-current',
                '[data-price]'
            ]
            
            price = None
            for selector in price_selectors:
                try:
                    price_element = element.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_element.text.strip()
                    price = self.extract_price_from_text(price_text)
                    if price:
                        break
                except NoSuchElementException:
                    continue
            
            if not price:
                logger.debug(f"Could not extract price for product: {product_name}")
                return None
            
            # קישור למוצר
            product_url = None
            try:
                link_element = element.find_element(By.CSS_SELECTOR, 'a')
                product_url = link_element.get_attribute('href')
                if product_url and not product_url.startswith('http'):
                    product_url = urljoin(self.base_url, product_url)
            except NoSuchElementException:
                pass
            
            # תמונה
            image_url = None
            try:
                img_element = element.find_element(By.CSS_SELECTOR, 'img')
                image_url = img_element.get_attribute('src') or img_element.get_attribute('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(self.base_url, image_url)
            except NoSuchElementException:
                pass
            
            # זמינות
            availability = "זמין"
            try:
                availability_selectors = [
                    '.availability',
                    '.stock-status',
                    '.in-stock',
                    '.out-of-stock'
                ]
                
                for selector in availability_selectors:
                    try:
                        avail_element = element.find_element(By.CSS_SELECTOR, selector)
                        avail_text = avail_element.text.strip().lower()
                        
                        if any(word in avail_text for word in ['אזל', 'לא זמין', 'out of stock']):
                            availability = "אזל מהמלאי"
                        elif any(word in avail_text for word in ['הזמנה', 'order']):
                            availability = "הזמנה מראש"
                        break
                    except NoSuchElementException:
                        continue
                        
            except Exception:
                pass
            
            return self.create_product_dict(
                name=product_name,
                price=price,
                url=product_url,
                image_url=image_url,
                availability=availability
            )
            
        except Exception as e:
            logger.error(f"Error extracting product data from KSP: {e}")
            return None
