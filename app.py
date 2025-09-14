#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Web Application - ממשק האינטרנט
"""

import logging
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sys
import os

# הוספת התיקייה הראשית ל-PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from core.price_finder import PriceFinder

# הגדרת logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# יצירת אפליקציית Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'price-hunter-secret-key'

# אתחול מנוע החיפוש
try:
    price_finder = PriceFinder()
    logger.info("PriceFinder initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize PriceFinder: {e}")
    price_finder = None

@app.route('/')
def index():
    """עמוד הבית"""
    return render_template('index.html')

@app.route('/search')
def search_page():
    """דף חיפוש עם תוצאות"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('index.html', error="לא הוכנס טקסט חיפוש")
    
    return render_template('search.html', query=query)

@app.route('/api/search', methods=['POST'])
def api_search():
    """API לחיפוש מוצרים"""
    if not price_finder:
        return jsonify({
            'success': False,
            'error': 'מערכת החיפוש לא זמינה כרגע'
        }), 503
    
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({
            'success': False,
            'error': 'חסרה מחרוזת חיפוש'
        }), 400
    
    query = data['query'].strip()
    if not query:
        return jsonify({
            'success': False,
            'error': 'מחרוזת חיפוש ריקה'
        }), 400
    
    max_results = data.get('max_results', 5)
    specific_stores = data.get('stores', [])
    
    try:
        logger.info(f"API search request: '{query}'")
        
        if specific_stores:
            results = price_finder.search_specific_stores(query, specific_stores, max_results)
        else:
            results = price_finder.search_all_stores(query, max_results)
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        logger.error(f"API search failed: {e}")
        return jsonify({
            'success': False,
            'error': 'שגיאה בביצוע החיפוש'
        }), 500

@app.route('/api/stores/status')
def api_stores_status():
    """בדיקת סטטוס החנויות"""
    if not price_finder:
        return jsonify({
            'success': False,
            'error': 'מערכת החיפוש לא זמינה'
        }), 503
    
    try:
        status = price_finder.get_store_status()
        return jsonify({
            'success': True,
            'stores': status
        })
    except Exception as e:
        logger.error(f"Failed to get store status: {e}")
        return jsonify({
            'success': False,
            'error': 'שגיאה בבדיקת סטטוס החנויות'
        }), 500

@app.route('/api/health')
def health_check():
    """בדיקת תקינות המערכת"""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': Config.VERSION,
        'price_finder': price_finder is not None
    }
    
    return jsonify(status)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    logger.info(f"Starting PriceHunter web application on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )