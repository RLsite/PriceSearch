#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Web Application - השרת הראשי של PriceHunter
הקובץ שהופך את הקוד לאתר אמיתי!

מה השרת הזה עושה:
1. מריץ אתר על http://localhost:5000
2. מקבל בקשות מדפדפנים של משתמשים
3. משתמש ב-PriceFinder לחיפוש במחירים
4. מחזיר דפי HTML יפים עם תוצאות
5. מספק API ל-JavaScript
"""

import logging
import sys
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

# הוספת הנתיבים לחיפוש המודולים
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# יבוא המודולים שלנו
try:
    from config import Config
    from core.price_finder import PriceFinder
except ImportError as e:
    print(f"❌ שגיאה בייבוא מודולים: {e}")
    print("🔍 בדוק שכל הקבצים קיימים ובמקום הנכון")
    sys.exit(1)

# הגדרת logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# יצירת אפליקציית Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'price-hunter-secret-key-change-in-production'
app.config['JSON_AS_ASCII'] = False  # תמיכה בעברית ב-JSON

# אתחול מנוע החיפוש
logger.info("🔍 מאתחל את PriceFinder...")
try:
    price_finder = PriceFinder()
    logger.info("✅ PriceFinder הותחל בהצלחה")
except Exception as e:
    logger.error(f"❌ כשלון באתחול PriceFinder: {e}")
    price_finder = None

# ===== ROUTES (נתיבים) =====

@app.route('/')
def index():
    """עמוד הבית - מה שהמשתמש רואה כשנכנס לאתר"""
    logger.info("🏠 משתמש נכנס לעמוד הבית")
    
    return '''
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PriceHunter - מציאת המחיר הטוב ביותר</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: rgba(255,255,255,0.1);
            padding: 50px;
            border-radius: 20px;
            text-align: center;
            max-width: 600px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        p {
            font-size: 1.2rem;
            margin-bottom: 30px;
            opacity: 0.9;
        }
        .search-form {
            margin: 30px 0;
        }
        input[type="text"] {
            padding: 15px 20px;
            font-size: 16px;
            border: none;
            border-radius: 25px;
            width: 350px;
            text-align: center;
            margin-bottom: 20px;
        }
        button {
            padding: 15px 30px;
            font-size: 18px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #218838;
        }
        .stores {
            margin-top: 40px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
        }
        .stores h3 {
            margin-bottom: 15px;
        }
        .store-list {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        .store-item {
            background: rgba(255,255,255,0.2);
            padding: 10px 15px;
            border-radius: 10px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 PriceHunter</h1>
        <p>מוצא את המחיר הטוב ביותר בכל החנויות</p>
        
        <div class="search-form">
            <form action="/search" method="get">
                <input type="text" 
                       name="q" 
                       placeholder="מה אתה מחפש? (iPhone, MacBook, אוזניות...)" 
                       required>
                <br>
                <button type="submit">🔍 חפש עכשיו</button>
            </form>
        </div>
        
        <div class="stores">
            <h3>החנויות שאנחנו סורקים:</h3>
            <div class="store-list">
                <div class="store-item">KSP</div>
                <div class="store-item">Bug</div>
                <div class="store-item">זאפ</div>
                <div class="store-item">Ivory</div>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@app.route('/search')
def search_page():
    """עמוד תוצאות חיפוש"""
    query = request.args.get('q', '').strip()
    
    if not query:
        logger.warning("⚠️  בקשת חיפוש ללא טקסט")
        return redirect(url_for('index'))
    
    logger.info(f"🔍 חיפוש דף עבור: '{query}'")
    
    if not price_finder:
        return '''
        <!DOCTYPE html>
        <html lang="he" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>שגיאה | PriceHunter</title>
        </head>
        <body style="font-family: Arial; text-align: center; padding: 50px; background: #f44336; color: white;">
            <h1>❌ שגיאה</h1>
            <p>מערכת החיפוש לא זמינה כרגע</p>
            <a href="/" style="color: white;">חזור לעמוד הבית</a>
        </body>
        </html>
        '''
    
    try:
        # ביצוע החיפוש
        logger.info(f"🚀 מתחיל חיפוש עבור: '{query}'")
        results = price_finder.search_all_stores(query, max_results_per_store=5)
        
        # בניית HTML עם התוצאות
        return build_results_html(query, results)
        
    except Exception as e:
        logger.error(f"❌ שגיאה בחיפוש: {e}")
        return f'''
        <!DOCTYPE html>
        <html lang="he" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>שגיאה בחיפוש | PriceHunter</title>
        </head>
        <body style="font-family: Arial; text-align: center; padding: 50px; background: #f44336; color: white;">
            <h1>❌ שגיאה בחיפוש</h1>
            <p>אירעה שגיאה בחיפוש עבור "{query}"</p>
            <p>שגיאה: {str(e)}</p>
            <a href="/" style="color: white;">חזור לעמוד הבית</a>
        </body>
        </html>
        '''

@app.route('/api/search', methods=['POST'])
def api_search():
    """API לחיפוש מוצרים - עבור JavaScript"""
    if not price_finder:
        return jsonify({
            'success': False,
            'error': 'מערכת החיפוש לא זמינה כרגע'
        }), 503
    
    # קבלת הנתונים מהבקשה
    try:
        data = request.get_json()
        if not data:
            raise ValueError("חסר JSON בבקשה")
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'פורמט בקשה שגוי'
        }), 400
    
    # בדיקת פרמטרים
    query = data.get('query', '').strip()
    if not query:
        return jsonify({
            'success': False,
            'error': 'חסרה מחרוזת חיפוש'
        }), 400
    
    max_results = data.get('max_results', 5)
    specific_stores = data.get('stores', [])
    
    try:
        logger.info(f"🔍 API חיפוש עבור: '{query}'")
        
        # ביצוע החיפוש
        if specific_stores:
            results = price_finder.search_specific_stores(query, specific_stores, max_results)
        else:
            results = price_finder.search_all_stores(query, max_results)
        
        # החזרת התוצאות
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        logger.error(f"❌ שגיאה ב-API: {e}")
        return jsonify({
            'success': False,
            'error': 'שגיאה בביצוע החיפוש'
        }), 500

@app.route('/api/health')
def health_check():
    """בדיקת תקינות המערכת"""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'price_finder_available': price_finder is not None,
        'active_scrapers': len(price_finder.scrapers) if price_finder else 0
    }
    
    return jsonify(status)

# ===== פונקציות עזר =====

def build_results_html(query, results):
    """בונה HTML עם תוצאות החיפוש"""
    
    # תחילת HTML
    html = f'''
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>תוצאות עבור: {query} | PriceHunter</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .back-btn {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            text-decoration: none;
            margin-bottom: 20px;
            transition: background 0.3s;
        }}
        .back-btn:hover {{
            background: rgba(255,255,255,0.3);
        }}
        .search-info {{
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        .product-card {{
            background: rgba(255,255,255,0.95);
            color: #333;
            margin: 20px 0;
            padding: 25px;
            border-radius: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.3s;
        }}
        .product-card:hover {{
            transform: translateY(-5px);
        }}
        .product-info {{
            flex: 1;
        }}
        .product-name {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 8px;
            color: #333;
        }}
        .store-info {{
            color: #666;
            margin-bottom: 5px;
            font-size: 1.1em;
        }}
        .price {{
            font-size: 2em;
            font-weight: bold;
            color: #e74c3c;
            text-align: left;
        }}
        .best-deal {{
            border: 3px solid #28a745;
            position: relative;
        }}
        .best-deal::before {{
            content: "🏆 המחיר הטוב ביותר";
            position: absolute;
            top: -15px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        .no-results h3 {{
            font-size: 2em;
            margin-bottom: 15px;
        }}
        .savings-info {{
            background: rgba(40, 167, 69, 0.2);
            border: 2px solid #28a745;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin: 20px 0;
        }}
        .error-info {{
            background: rgba(220, 53, 69, 0.2);
            border: 2px solid #dc3545;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 PriceHunter</h1>
            <a href="/" class="back-btn">🏠 עמוד הבית</a>
        </div>
        
        <div class="search-info">
            <h2>תוצאות עבור: "{query}"</h2>
            <p>נמצאו {results['total_products']} מוצרים ב-{results['search_time']} שניות</p>
            <p>נבדקו החנויות: {', '.join(results['stores_searched'])}</p>
        </div>
    '''
    
    # אם יש שגיאות - הצג אותן
    if results.get('errors'):
        html += '<div class="error-info"><h4>⚠️ התרחשו בעיות:</h4><ul>'
        for error in results['errors']:
            html += f'<li>{error}</li>'
        html += '</ul></div>'
    
    # הוספת התוצאות
    if results['total_products'] == 0:
        html += '''
            <div class="no-results">
                <h3>😔 לא נמצאו תוצאות</h3>
                <p>נסה מילות חיפוש אחרות או פשוטות יותר</p>
                <p><strong>טיפים לחיפוש טוב יותר:</strong></p>
                <ul style="list-style: none; padding: 0;">
                    <li>✓ נסה רק את שם המוצר: "iPhone" במקום "iPhone 15 Pro Max"</li>
                    <li>✓ השתמש במילים באנגלית: "MacBook" במקום "מקבוק"</li>
                    <li>✓ בדוק את הכתיב</li>
                </ul>
            </div>
        '''
    else:
        # מציאת המחיר הטוב ביותר
        best_price = min(p['price'] for p in results['products'])
        
        # הוספת כל מוצר
        for product in results['products']:
            is_best = (product['price'] == best_price)
            
            html += f'''
                <div class="product-card {'best-deal' if is_best else ''}">
                    <div class="product-info">
                        <div class="product-name">{product['name']}</div>
                        <div class="store-info">🏪 {product['store']} | 📦 {product.get('availability', 'זמין')}</div>
                    </div>
                    <div class="price">₪{product['price']:,.0f}</div>
                </div>
            '''
        
        # הוספת מידע על חיסכון
        if results.get('best_deal') and results['best_deal'].get('savings'):
            savings = results['best_deal']['savings']
            savings_percent = results['best_deal'].get('savings_percent', 0)
            html += f'''
                <div class="savings-info">
                    <h3>💰 חיסכון מעולה!</h3>
                    <p>המחיר הטוב ביותר חוסך לך <strong>₪{savings:,.0f}</strong></p>
                    <p>זה <strong>{savings_percent}%</strong> פחות מהחנות הכי יקרה!</p>
                </div>
            '''
    
    # סגירת HTML
    html += '''
        </div>
    </body>
    </html>
    '''
    
    return html

# ===== טיפול בשגיאות =====

@app.errorhandler(404)
def not_found(error):
    """עמוד לא נמצא"""
    return '''
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head><meta charset="UTF-8"><title>עמוד לא נמצא</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🔍 עמוד לא נמצא</h1>
        <p>הדף שחיפשת לא קיים</p>
        <a href="/">חזור לעמוד הבית</a>
    </body>
    </html>
    ''', 404

@app.errorhandler(500)
def internal_error(error):
    """שגיאת שרת"""
    logger.error(f"שגיאת שרת: {error}")
    return '''
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head><meta charset="UTF-8"><title>שגיאת שרת</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px; background: #f44336; color: white;">
        <h1>❌ שגיאת שרת</h1>
        <p>אירעה שגיאה במערכת</p>
        <a href="/" style="color: white;">חזור לעמוד הבית</a>
    </body>
    </html>
    ''', 500

# ===== הפעלת השרת =====

if __name__ == '__main__':
    logger.info(f"""
🚀 PriceHunter Web Server Starting...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 אתר זמין על: http://127.0.0.1:5000
🔍 חנויות זמינות: {len(price_finder.scrapers) if price_finder else 0}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
לעצירה: Ctrl+C
    """)
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=True)
    except KeyboardInterrupt:
        logger.info("👋 שרת נעצר")
    except Exception as e:
        logger.error(f"❌ שגיאה בהפעלת השרת: {e}")
