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

Routes (נתיבים) שהשרת מכיר:
- GET /                    ← עמוד הבית
- GET /search?q=iPhone     ← עמוד תוצאות
- POST /api/search         ← API לחיפוש
- GET /api/health          ← בדיקת תקינות
- GET /api/stores/status   ← סטטוס חנויות
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

def create_app():
    """
    יצירת אפליקציית Flask
    
    למה פונקציה נפרדת?
    - קל לבדיקות
    - אפשר ליצור כמה אפליקציות
    - הגדרות גמישות
    """
    # יצירת אפליקציית Flask
    app = Flask(__name__)
    
    # הגדרות האפליקציה
    app.config['SECRET_KEY'] = 'price-hunter-secret-key-change-in-production'
    app.config['JSON_AS_ASCII'] = False  # תמיכה בעברית ב-JSON
    
    return app

# יצירת האפליקציה
app = create_app()

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
    """
    עמוד הבית - מה שהמשתמש רואה כשנכנס לאתר
    
    Returns:
        דף HTML של עמוד הבית
    """
    logger.info("🏠 משתמש נכנס לעמוד הבית")
    
    # בהמשך נוסיף קובץ templates/index.html
    # כרגע נחזיר הודעה פשוטה
    return """
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>PriceHunter - מציאת המחיר הטוב ביותר</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 20px;
                max-width: 600px;
                margin: 0 auto;
            }
            input {
                padding: 15px;
                font-size: 16px;
                border: none;
                border-radius: 25px;
                width: 300px;
                text-align: center;
            }
            button {
                padding: 15px 30px;
                font-size: 16px;
                background: #28a745;
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                margin: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 PriceHunter</h1>
            <p>מוצא את המחיר הטוב ביותר בכל החנויות</p>
            
            <form action="/search" method="get">
                <input type="text" name="q" placeholder="מה אתה מחפש? (iPhone, MacBook...)" required>
                <br><br>
                <button type="submit">🔍 חפש עכשיו</button>
            </form>
            
            <div style="margin-top: 30px;">
                <h3>החנויות שאנחנו סורקים:</h3>
                <p>KSP | Bug | זאפ | Ivory</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/search')
def search_page():
    """
    עמוד תוצאות חיפוש
    
    Query Parameters:
        q: מה לחפש (חובה)
        
    Returns:
        דף HTML עם תוצאות החיפוש
    """
    query = request.args.get('q', '').strip()
    
    if not query:
        logger.warning("⚠️  בקשת חיפוש ללא טקסט")
        return redirect(url_for('index'))
    
    logger.info(f"🔍 חיפוש דף עבור: '{query}'")
    
    if not price_finder:
        return """
        <h1>❌ שגיאה</h1>
        <p>מערכת החיפוש לא זמינה כרגע</p>
        <a href="/">חזור לעמוד הבית</a>
        """
    
    try:
        # ביצוע החיפוש
        logger.info(f"🚀 מתחיל חיפוש עבור: '{query}'")
        results = price_finder.search_all_stores(query, max_results_per_store=5)
        
        # בניית HTML עם התוצאות
        html_results = build_results_html(query, results)
        return html_results
        
    except Exception as e:
        logger.error(f"❌ שגיאה בחיפוש: {e}")
        return f"""
        <h1>❌ שגיאה בחיפוש</h1>
        <p>אירעה שגיאה בחיפוש עבור "{query}"</p>
        <p>שגיאה: {str(e)}</p>
        <a href="/">חזור לעמוד הבית</a>
        """

@app.route('/api/search', methods=['POST'])
def api_search():
    """
    API לחיפוש מוצרים - עבור JavaScript
    
    Request Body (JSON):
        {
            "query": "iPhone 15",
            "max_results": 5,
            "stores": ["ksp", "bug"] // אופציונלי
        }
        
    Returns:
        JSON עם התוצאות
    """
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

@app.route('/api/stores/status')
def api_stores_status():
    """
    בדיקת סטטוס כל החנויות
    
    Returns:
        JSON עם סטטוס כל חנות
    """
    if not price_finder:
        return jsonify({
            'success': False,
            'error': 'מערכת החיפוש לא זמינה'
        }), 503
    
    try:
        logger.info("🏥 בודק סטטוס חנויות")
        status = price_finder.get_store_status()
        
        return jsonify({
            'success': True,
            'stores': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ שגיאה בבדיקת סטטוס: {e}")
        return jsonify({
            'success': False,
            'error': 'שגיאה בבדיקת סטטוס החנויות'
        }), 500

@app.route('/api/health')
def health_check():
    """
    בדיקת תקינות המערכת - עבור ניטור
    
    Returns:
        JSON עם מידע על תקינות המערכת
    """
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': Config.VERSION,
        'price_finder_available': price_finder is not None,
        'active_scrapers': len(price_finder.scrapers) if price_finder else 0
    }
    
    return jsonify(status)

# ===== פונקציות עזר =====

def build_results_html(query, results):
    """
    בונה HTML עם תוצאות החיפוש
    
    Args:
        query: מה חיפשנו
        results: תוצאות מ-PriceFinder
        
    Returns:
        HTML string
    """
    html = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>תוצאות עבור: {query} | PriceHunter</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .search-info {{
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 20px;
                text-align: center;
            }}
            .product-card {{
                background: rgba(255,255,255,0.95);
                color: #333;
                margin: 15px 0;
                padding: 20px;
                border-radius: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .product-info {{
                flex: 1;
            }}
            .product-name {{
                font-size: 1.2em;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .store-info {{
                color: #666;
                margin-bottom: 5px;
            }}
            .price {{
                font-size: 1.5em;
                font-weight: bold;
                color: #e74c3c;
            }}
            .best-deal {{
                border: 3px solid #28a745;
                position: relative;
            }}
            .best-deal::before {{
                content: "🏆 המחיר הטוב ביותר";
                position: absolute;
                top: -10px;
                right: 20px;
                background: #28a745;
                color: white;
                padding: 5px 15px;
                border-radius: 15px;
                font-size: 0.9em;
            }}
            .no-results {{
                text-align: center;
                padding: 50px;
            }}
            .back-btn {{
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                margin: 20px;
                text-decoration: none;
                display: inline-block;
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
                <p>נבדקו: {', '.join(results['stores_searched'])}</p>
            </div>
    """
    
    # הוספת התוצאות
    if results['total_products'] == 0:
        html += """
            <div class="no-results">
                <h3>😔 לא נמצאו תוצאות</h3>
                <p>נסה מילות חיפוש אחרות</p>
            </div>
        """
    else:
        # הוספת כל מוצר
        best_price = min(p['price'] for p in results['products']) if results['products'] else 0
        
        for product in results['products']:
            is_best = product['price'] == best_price
            
            html += f"""
                <div class="product-card {'best-deal' if is_best else ''}">
                    <div class="product-info">
                        <div class="product-name">{product['name']}</div>
                        <div class="store-info">🏪 {product['store']} | 📦 {product.get('availability', 'זמין')}</div>
                    </div>
                    <div class="price">₪{product['price']:,.0f}</div>
                </div>
            """
        
        # הוספת מידע על חיסכון
        if results.get('best_deal') and results['best_deal'].get('savings'):
            savings = results['best_deal']['savings']
            html += f"""
                <div class="search-info">
                    <h3>💰 חיסכון</h3>
                    <p>המחיר הטוב ביותר חוסך לך ₪{savings:,.0f}!</p>
                </div>
            """
    
    # סגירת HTML
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

# ===== טיפול בשגיאות =====

@app.errorhandler(404)
def not_found(error):
    """עמוד לא נמצא"""
    return """
    <h1>🔍 עמוד לא נמצא</h1>
    <p>הדף שחיפשת לא קיים</p>
    <a href="/">חזור לעמוד הבית</a>
    """, 404

@app.errorhandler(500)
def internal_error(error):
    """שגיאת שרת"""
    logger.error(f"שגיאת שרת: {error}")
    return """
    <h1>❌ שגיאת שרת</h1>
    <p>אירעה שגיאה במערכת</p>
    <a href="/">חזור לעמוד הבית</a>
    """, 500

# ===== הפעלת השרת =====

if __name__ == '__main__':
    logger.info(f"""
🚀 PriceHunter Web Server Starting...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 אתר זמין על: http://127.0.0.1:5000
🔍 חנויות זמינות: {len(price_finder.scrapers) if price_finder else 0}
⚡ מצב debug: {Config.DEBUG}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
לעצירה: Ctrl+C
    """)
    
    try:
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=Config.DEBUG
        )
    except KeyboardInterrupt:
        logger.info("👋 שרת נעצר")
    except Exception as e:
        logger.error(f"❌ שגיאה בהפעלת השרת: {e}")
