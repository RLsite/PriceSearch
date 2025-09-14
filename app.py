#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PriceHunter - מערכת השוואת מחירים
הקובץ הראשי של האפליקציה
"""

import logging
import sys
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# הוספת נתיב הפרויקט
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ייבוא המודולים שלנו
try:
    from config import Config
    from core.price_finder import PriceFinder
except ImportError as e:
    print(f"❌ שגיאת ייבוא: {e}")
    print("💡 ודא שהקבצים config.py ו-core/price_finder.py קיימים")
    sys.exit(1)

# הגדרת logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# יצירת Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.config['JSON_AS_ASCII'] = False  # תמיכה בעברית

# אתחול מנוע החיפוש
logger.info("🔍 מאתחל PriceFinder...")
try:
    price_finder = PriceFinder()
    logger.info(f"✅ PriceFinder מוכן עם {len(price_finder.scrapers)} חנויות")
except Exception as e:
    logger.error(f"❌ שגיאה באתחול PriceFinder: {e}")
    price_finder = None

# ===== נתיבי האפליקציה =====

@app.route('/')
def home():
    """עמוד הבית"""
    logger.info("👤 משתמש נכנס לעמוד הבית")
    
    # נתוני סטטיסטיקה לעמוד הבית
    stats = {
        'active_stores': len(price_finder.scrapers) if price_finder else 0,
        'total_searches': 0,  # נוסיף מעקב בעתיד
        'average_savings': 15  # נוסיף חישוב אמיתי
    }
    
    return render_template('home.html', stats=stats)

@app.route('/search')
def search():
    """עמוד תוצאות החיפוש"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('home.html', error="אנא הכנס מוצר לחיפוש")
    
    if not price_finder:
        return render_template('error.html', 
                             title="מערכת לא זמינה",
                             message="מערכת החיפוש אינה פעילה כרגע")
    
    logger.info(f"🔍 חיפוש: '{query}'")
    
    try:
        # ביצוע החיפוש
        results = price_finder.search_all_stores(query, max_results_per_store=5)
        
        # הכנת נתונים לתצוגה
        search_data = {
            'query': query,
            'results': results,
            'has_results': results['total_products'] > 0,
            'search_time': results.get('search_time', 0),
            'stores_count': len(results.get('stores_searched', []))
        }
        
        return render_template('search_results.html', **search_data)
        
    except Exception as e:
        logger.error(f"❌ שגיאה בחיפוש '{query}': {e}")
        return render_template('error.html',
                             title="שגיאה בחיפוש", 
                             message=f"לא הצלחנו לחפש את '{query}'",
                             details=str(e))

@app.route('/api/search', methods=['POST'])
def api_search():
    """API לחיפוש - עבור JavaScript"""
    if not price_finder:
        return jsonify({'error': 'מערכת החיפוש לא זמינה'}), 503
    
    data = request.get_json()
    if not data or not data.get('query'):
        return jsonify({'error': 'חסרה מחרוזת חיפוש'}), 400
    
    query = data['query'].strip()
    max_results = data.get('max_results', 5)
    
    try:
        logger.info(f"🔍 API חיפוש: '{query}'")
        results = price_finder.search_all_stores(query, max_results)
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        logger.error(f"❌ API שגיאה: {e}")
        return jsonify({'error': 'שגיאה בביצוע החיפוש'}), 500

@app.route('/api/stores')
def api_stores():
    """מידע על החנויות הזמינות"""
    if not price_finder:
        return jsonify({'error': 'מערכת לא זמינה'}), 503
    
    try:
        stores_status = price_finder.get_store_status()
        return jsonify({
            'success': True,
            'stores': stores_status
        })
    except Exception as e:
        logger.error(f"❌ שגיאה בקבלת סטטוס חנויות: {e}")
        return jsonify({'error': 'שגיאה בקבלת מידע חנויות'}), 500

@app.route('/health')
def health_check():
    """בדיקת בריאות המערכת"""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': Config.VERSION,
        'price_finder_active': price_finder is not None,
        'active_scrapers': len(price_finder.scrapers) if price_finder else 0
    }
    
    return jsonify(status)

@app.route('/about')
def about():
    """עמוד אודות"""
    return render_template('about.html')

# ===== טיפול בשגיאות =====

@app.errorhandler(404)
def not_found(error):
    """עמוד לא נמצא"""
    return render_template('error.html',
                         title="עמוד לא נמצא", 
                         message="הדף שחיפשת לא קיים",
                         code=404), 404

@app.errorhandler(500)
def server_error(error):
    """שגיאת שרת"""
    logger.error(f"שגיאת שרת: {error}")
    return render_template('error.html',
                         title="שגיאת שרת",
                         message="אירעה שגיאה במערכת",
                         code=500), 500

@app.errorhandler(503)
def service_unavailable(error):
    """שירות לא זמין"""
    return render_template('error.html',
                         title="שירות לא זמין",
                         message="המערכת בתחזוקה, אנא נסה מאוחר יותר",
                         code=503), 503

# ===== הפעלת השרת =====

if __name__ == '__main__':
    logger.info(f"""
🚀 PriceHunter מתחיל...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 כתובת: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}
🏪 חנויות זמינות: {len(price_finder.scrapers) if price_finder else 0}
🔧 מצב debug: {Config.FLASK_DEBUG}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    try:
        app.run(
            host=Config.FLASK_HOST,
            port=Config.FLASK_PORT,
            debug=Config.FLASK_DEBUG
        )
    except KeyboardInterrupt:
        logger.info("👋 השרת נעצר על ידי המשתמש")
    except Exception as e:
        logger.error(f"❌ שגיאה בהפעלת השרת: {e}")
