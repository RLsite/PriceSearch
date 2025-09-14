#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Package - ממשק המשתמש של PriceHunter
כאן חיים האתר והAPI שהמשתמשים רואים

מבנה התיקייה:
├── web/
│   ├── __init__.py          ← זה הקובץ
│   ├── app.py               ← שרת Flask הראשי
│   ├── templates/           ← דפי HTML
│   │   ├── index.html       ← עמוד הבית
│   │   ├── results.html     ← עמוד תוצאות
│   │   └── error.html       ← עמוד שגיאות
│   └── static/              ← קבצים סטטיים
│       ├── css/
│       │   └── style.css    ← עיצוב
│       ├── js/
│       │   └── script.js    ← JavaScript
│       └── images/          ← תמונות

איך זה עובד:
1. Flask מריץ שרת אינטרנט
2. המשתמש נכנס לכתובת (http://localhost:5000)
3. Flask מחזיר דפי HTML יפים
4. JavaScript שולח בקשות ל-API
5. API משתמש ב-PriceFinder לחיפוש
6. התוצאות חוזרות למשתמש

זה כמו מסעדה:
- templates/ = התפריט (מה המשתמש רואה)
- static/ = העיצוב והאווירה
- app.py = המלצר (מקבל הזמנות ומביא אוכל)
- PriceFinder = המטבח (מכין את האוכל)
"""

# ייבוא הרכיבים הראשיים
try:
    from .app import app, create_app
except ImportError:
    # עוד לא קיים - נוסיף בשלב הבא
    app = None
    create_app = None

# מידע על החבילה
__version__ = '1.0.0'
__description__ = 'Web interface for PriceHunter'

# מה ציבורי בחבילה זו
__all__ = [
    'app',           # האפליקציה הראשית
    'create_app'     # פונקציה ליצירת אפליקציה
]
