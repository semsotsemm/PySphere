import random
import psycopg2
from psycopg2 import extensions
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor

USER_NAME = "postgres"
PASSWORD = "5329965"
DB_NAME = "courses_db"


def run_query(db, sql, params=None, is_select=False):
    with psycopg2.connect(
        dbname=db, user=USER_NAME, password=PASSWORD, host="127.0.0.1"
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if is_select:
                return cur.fetchone()


def check_db_exists(name):
    result = run_query(
        "postgres", "SELECT 1 FROM pg_database WHERE datname = %s", (name,), True
    )
    return result is not None


def create_database(name):
    conn = psycopg2.connect(dbname="postgres", user=USER_NAME, password=PASSWORD)
    conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE {name}")
    conn.close()
    print(f"База {name} создана.")


def check_table_exists(db, table):
    sql = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)"
    result = run_query(db, sql, (table,), True)
    return result[0] if result else False


def create_course_table(db):
    sql = """
        CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            old_price DECIMAL(10, 2),
            new_price DECIMAL(10, 2),
            discount_percent INTEGER,
            avatar_url TEXT,
            main_advantage TEXT,
            advantages TEXT[],  
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    run_query(db, sql)


def create_lessons_table(db):
    sql = """
        CREATE TABLE IF NOT EXISTS lessons (
            id SERIAL PRIMARY KEY,
            course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            content TEXT
        );
    """
    run_query(db, sql)
    print("Таблица 'products' готова.")


def add_data(db_name, user, password):
    conn = psycopg2.connect(dbname=db_name, user=user, password=password)
    cur = conn.cursor()

    adv_list = [
        "Доступ навсегда",
        "Чат с куратором",
        "Сертификат",
        "5 проектов в портфолио",
    ]

    cur.execute(
        """
        INSERT INTO courses (title, advantages, new_price) 
        VALUES (%s, %s, %s) RETURNING id
    """,
        ("Python Pro", adv_list, 15000),
    )

    course_id = cur.fetchone()[0]

    lessons_data = [
        ("Введение", "Установка окружения"),
        ("Типы данных", "Списки и словари"),
        ("Функции", "Аргументы и декораторы"),
    ]

    for title, content in lessons_data:
        cur.execute(
            "INSERT INTO lessons (course_id, title, content) VALUES (%s, %s, %s)",
            (course_id, title, content),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("Данные успешно добавлены!")


def create_users_table(db):
    sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    run_query(db, sql)


def create_orders_table(db):
    sql_users = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255),
            email VARCHAR(255),
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    sql_orders = """
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            course_id INTEGER REFERENCES courses(id),
            amount DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    run_query(db, sql_users)
    run_query(db, sql_orders)


def mock_data_if_empty(db_name):
    with psycopg2.connect(
        dbname=db_name, user=USER_NAME, password=PASSWORD, host="127.0.0.1"
    ) as conn:
        with conn.cursor() as cur:
            # 1. Сначала проверим, есть ли хоть один курс
            cur.execute("SELECT id FROM courses LIMIT 1")
            course = cur.fetchone()

            if not course:
                # Если курсов нет, создаем один, чтобы было к чему привязать продажи
                print("Создаем тестовый курс для аналитики...")
                cur.execute(
                    "INSERT INTO courses (title, description, old_price, new_price) "
                    "VALUES (%s, %s, %s, %s) RETURNING id",
                    ("Python Core", "Тестовый курс для графиков", 10000, 7500),
                )
                course_id = cur.fetchone()[0]
            else:
                course_id = course[0]

            # 2. Теперь проверяем, есть ли заказы
            cur.execute("SELECT COUNT(*) FROM orders")
            if cur.fetchone()[0] > 0:
                return

            print(f"Генерируем продажи для курса ID: {course_id}...")
            # Создаем фейковые продажи за последние 7 дней
            for i in range(50):
                days_ago = random.randint(0, 7)
                amount = random.choice([7500, 15000, 5000, 12000])
                date = datetime.now() - timedelta(days=days_ago)
                cur.execute(
                    "INSERT INTO orders (course_id, amount, created_at) VALUES (%s, %s, %s)",
                    (course_id, amount, date),
                )

            # 3. Добавим фейкового юзера для статистики "Всего пользователей"
            cur.execute("SELECT COUNT(*) FROM users")
            if cur.fetchone()[0] == 0:
                cur.execute(
                    "INSERT INTO users (username, last_active) VALUES ('admin_test', NOW())"
                )

            conn.commit()


def get_dashboard_stats(db_name):
    """Собирает всю статистику для админки"""
    with psycopg2.connect(
        dbname=db_name, user=USER_NAME, password=PASSWORD, host="127.0.0.1"
    ) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            # 1. Общая выручка
            cur.execute("SELECT SUM(amount) as total_revenue FROM orders")
            total_revenue = cur.fetchone()["total_revenue"] or 0

            # 2. Количество пользователей
            cur.execute("SELECT COUNT(*) as total_users FROM users")
            total_users = cur.fetchone()["total_users"]

            # 3. Продажи по дням (для графика)
            cur.execute(
                """
                SELECT DATE(created_at) as date, SUM(amount) as sum 
                FROM orders 
                GROUP BY DATE(created_at) 
                ORDER BY DATE(created_at) ASC 
                LIMIT 7
            """
            )
            sales_chart = cur.fetchall()

            return {
                "total_revenue": total_revenue,
                "total_users": total_users,
                "sales_chart": sales_chart,
                "online_users": random.randint(
                    5, 40
                ),  # Имитация онлайна (т.к. нет вебсокетов)
            }


def get_users_count(db_name):
    with psycopg2.connect(
        dbname=db_name, user=USER_NAME, password=PASSWORD, host="127.0.0.1"
    ) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("SELECT COUNT(*) FROM users")
                return cur.fetchone()[0]
            except:
                return 0


def delete_course(db_name, course_id):
    with psycopg2.connect(
        dbname=db_name, user=USER_NAME, password=PASSWORD, host="127.0.0.1"
    ) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("DELETE FROM courses WHERE id = %s", (course_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error deleting: {e}")
                conn.rollback()
                return False


def enter_new_course(db_name, course_data):
    with psycopg2.connect(
        dbname=db_name, user=USER_NAME, password=PASSWORD, host="127.0.0.1"
    ) as conn:
        with conn.cursor() as cur:
            try:
                if course_data.old_price != 0:
                    discount_percent = (
                        100 - 100 * course_data.new_price / course_data.old_price
                    )
                else:
                    discount_percent = 0
                cur.execute(
                    """
                    INSERT INTO courses (title, description, old_price, new_price, discount_percent, avatar_url, main_advantage, advantages)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;""",
                    (
                        course_data.title,
                        course_data.description,
                        course_data.old_price,
                        course_data.new_price,
                        discount_percent,
                        course_data.avatar_url,
                        course_data.main_advantage,
                        course_data.advantages,
                    ),
                )
                new_course_id = cur.fetchone()[0]

                for lesson in course_data.lessons:
                    cur.execute(
                        """INSERT INTO lessons (course_id, title, content) 
                        VALUES (%s, %s, %s)""",
                        (new_course_id, lesson.title, lesson.content),
                    )
                conn.commit()
                return new_course_id
            except Exception as e:
                conn.rollback()
                print(f"Ошибка при записи: {e}")
                return None


def get_all_courses(db_name):
    with psycopg2.connect(
        dbname=db_name, user=USER_NAME, password=PASSWORD, host="127.0.0.1"
    ) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM courses")
            return cur.fetchall()


if __name__ == "__main__":
    if not check_db_exists(DB_NAME):
        create_database(DB_NAME)
    else:
        print(f"База {DB_NAME} уже существует.")

    if not check_table_exists(DB_NAME, "courses"):
        create_course_table(DB_NAME)
    else:
        print("Таблица 'courses' уже существует.")

    if not check_table_exists(DB_NAME, "lessons"):
        create_lessons_table(DB_NAME)
    else:
        print("Таблица 'lessons' уже существует.")
