import sqlite3
from fuzzywuzzy import process

# Подключение к базе данных
conn = sqlite3.connect('messages.db')
cursor = conn.cursor()

# Создание таблицы, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT,
    category TEXT
)
''')

def classify_message(message):
    categories = {
        "изменение тарифа": ["изменить тариф", "тариф", "смена тарифа", "поменять тариф", "сменить", "смена"],
        "заключение договора": ["заключить договор", "договор", "подписать договор", "договориться"],
        "подключение услуги": ["подключить услугу", "услуга", "подключение", "активировать", "подключить интернет"]
    }

    message_lower = message.lower()
    best_match, score = process.extractOne(message_lower, [keyword for keywords in categories.values() for keyword in keywords])

    threshold = 70 
    if score >= threshold:
        for category, keywords in categories.items():
            if best_match in keywords:
                return category

    return "Не удалось классифицировать сообщение"

def save_message(message, category):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (message, category) VALUES (?, ?)', (message, category))
    conn.commit()

def close_connection():
    conn.close()
