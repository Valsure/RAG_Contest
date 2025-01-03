import sqlite3

def init_sqlite_db():
    db_file = 'database1.db'  
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            name VARCHAR(50),
            id INT PRIMARY KEY,
            age INT,
            job VARCHAR(50),
            gender VARCHAR(10)
        )
    ''')

    cursor.executemany('''
        INSERT OR IGNORE INTO users (name, id, age, job, gender) VALUES (?, ?, ?, ?, ?)
    ''', [
        ('Jason', 0, 24, 'Engineer', '男'),
        ('Alice', 1, 18, 'Student', '女'),
        ('Bob', 2, 20, 'worker', '男'),
        ('李梓衡', 3, 24, '学生', '男'),
        ('SpongeBob', 4, 15, 'Sponge', '男'),
        ('小美', 5, 19, 'Student', '女')
    ])

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_sqlite_db()
    print("SQLite 数据库已初始化")
