import sqlite3

def create_connection(db_file):
    """Создает соединение с SQLite базой данных."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Соединение с базой данных прошло успешно!")
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """Создает таблицу клиентов в базе данных."""
    try:
        sql_create_clients_table = """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_number TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            phone_number TEXT NOT NULL
        );
        """
        cursor = conn.cursor()
        cursor.execute(sql_create_clients_table)
        print("Таблица клиентов создана успешно!")
    except sqlite3.Error as e:
        print(e)

def insert_client(conn, client):
    """Вставляет нового клиента в таблицу clients."""
    sql = ''' INSERT INTO clients(contract_number, name, phone_number)
              VALUES(?, ?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, client)
    conn.commit()
    return cur.lastrowid

def find_client_by_contract_number(conn, contract_number):
    """Ищет клиента по номеру договора."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM clients WHERE contract_number=?", (contract_number,)) # ищу именно имя 
    result = cursor.fetchone()
    return result[0] if result else None

def main():
    database = "clients.db"  # имя файла базы данных

    # создаем соединение с базой данных
    conn = create_connection(database)

    # создаем таблицу, если она не существует
    if conn is not None:
        create_table(conn)

        # пример данных для вставки (номер договора, имя клиента, номер телефона)
        clients_data = [
            ('516111111', 'Иван Иванов', '+79161234567'),
            ('516111112', 'Петр Петров', '+79161234568'),
            ('516111113', 'Сергей Сергеев', '+79161234569'),
            ('516111114', 'Алексей Алексеев', '+79161234570'),
            ('516111115', 'Мария Мариева', '+79161234571'),
            ('516111116', 'Елена Еленова', '+79161234572'),
            ('516111117', 'Алиса Олеговна', '+79161234573'),
            ('516111118', 'Алексей Витальевич', '+79161234574'),
            ('516111119', 'Ольга Ольгина', '+79161234575'),
        ]

        # вставляем клиентов
        for client in clients_data:
            try:
                insert_client(conn, client)
            except sqlite3.IntegrityError:
                print(f"Клиент с номером договора {client[0]} уже существует!")

        print("Все клиенты добавлены в базу данных.")
        
        # закрываем соединение
        conn.close()
    else:
        print("Ошибка! Невозможно создать соединение с базой данных.")

if __name__ == '__main__':
    main()
