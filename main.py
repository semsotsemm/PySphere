import uvicorn
import database as db
import secrets
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Разрешаем запросы с фронтенда (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

# --- НАСТРОЙКИ БЕЗОПАСНОСТИ ---
ADMIN_USER = "admin"
ADMIN_PASS = "admin123" # ПОМЕНЯЙ НА СЛОЖНЫЙ ПАРОЛЬ!

def check_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Проверяет логин и пароль администратора"""
    is_correct_username = secrets.compare_digest(credentials.username, ADMIN_USER)
    is_correct_password = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/admin/dashboard-data/")
def get_dashboard_data(username: str = Depends(check_admin)):
    # Создаем таблицы и фейк данные, если их нет
    db.create_orders_table("courses_db")
    db.mock_data_if_empty("courses_db")
    
    stats = db.get_dashboard_stats("courses_db")
    
    # Преобразуем даты в строки для JSON
    chart_labels = [str(row['date']) for row in stats['sales_chart']]
    chart_values = [float(row['sum']) for row in stats['sales_chart']]
    
    return {
        "summary": {
            "revenue": stats['total_revenue'],
            "users": stats['total_users'],
            "online": stats['online_users'],
            "courses": len(db.get_all_courses("courses_db"))
        },
        "chart": {
            "labels": chart_labels,
            "values": chart_values
        }
    }

# --- СХЕМЫ ---
class LessonSchema(BaseModel):
    title: str
    content: str

class CourseSchema(BaseModel):
    title: str
    description: str
    old_price: float
    new_price: float
    avatar_url: str
    main_advantage: str
    advantages: list[str]
    lessons: list[LessonSchema]

# --- API ---

@app.get("/get-all-courses/")
def get_all_courses():
    data = db.get_all_courses(db_name="courses_db")
    return data

@app.get("/get-stats/")
def get_stats():
    """Возвращает статистику (кол-во пользователей)"""
    # Для теста создадим таблицу пользователей, если её нет
    if not db.check_table_exists("courses_db", "users"):
        db.create_users_table("courses_db")
        
    users = db.get_users_count(db_name="courses_db")
    return {"users_count": users}

# ЗАЩИЩЕННЫЙ МЕТОД (Требует пароль)
@app.post("/add-new-course/")
def add_new_course(course: CourseSchema, username: str = Depends(check_admin)):
    print(f"Админ {username} добавляет курс {course.title}")
    result_id = db.enter_new_course(db_name="courses_db", course_data=course)
    if result_id:
        return {"status": "success", "id": result_id}
    else:
        return {"status": "error", "message": "Не удалось сохранить курс"}

# ЗАЩИЩЕННЫЙ МЕТОД (Требует пароль)
@app.delete("/delete-course/{course_id}")
def delete_course(course_id: int, username: str = Depends(check_admin)):
    result = db.delete_course(db_name="courses_db", course_id=course_id)
    if result:
        return {"status": "success", "message": f"Курс {course_id} удален"}
    else:
        raise HTTPException(status_code=400, detail="Ошибка удаления")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)