from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
import re
import os

app = FastAPI()

client = AsyncIOMotorClient(os.getenv('DB'))  # Подключение к MongoDB
db = client['webappDB']  # Предполагая, что ваша база данных называется 'webappDB'
collection = db['templates_collection']  # Предполагая, что шаблоны форм хранятся в коллекции 'form_templates'

class FormData(BaseModel):
    name: str = Field(..., title="The name of the form")
    fields: dict = Field(..., title="The fields of the form")

EXPECTED_FIELD_TYPES = {
    "phone": "phone",
    "email": "email",
    # добавьте здесь другие поля и их ожидаемые типы
}

@app.post("/create_form")
async def create_form(form_data: FormData):
    # Шаг 1: Валидация
    validation_errors = []
    for field, value in form_data.fields.items():
        field_type = find_field_type(value)
        if field_type != EXPECTED_FIELD_TYPES.get(field):
            validation_errors.append(
                f"Validation error in field '{field}': expected type '{EXPECTED_FIELD_TYPES.get(field)}', got '{field_type}'")
    if validation_errors:
        return {"validation_errors": validation_errors}

    # Шаг 2: Добавление даты
    form_data.fields["date"] = datetime.now().isoformat()

    # Шаг 3: Сохранение формы
    await collection.insert_one(form_data.dict(by_alias=True))
    return {"success": "Form saved successfully"}



@app.post("/get_form")
async def get_form(form_data: FormData):
   # Шаг 1: Проверка наличия формы
   form_template = await collection.find_one({
       "name": form_data.name,
       "fields.phone": form_data.fields.get('phone'),
       "fields.email": form_data.fields.get('email')
   })
   if form_template:
       return form_template['fields']

   return {"error": "Форма не найдена"}



def find_field_type(value):
    if is_date(value):
        return "date"
    elif is_phone(value):
        return "phone"
    elif is_email(value):
        return "email"
    else:
        return "text"

def is_date(value):
    # Проверьте, является ли значение датой
    date_patterns = ["\d{2}\.\d{2}\.\d{4}", "\d{4}\-\d{2}\-\d{2}"]
    if any(re.match(pattern, value) for pattern in date_patterns):
        return True
    return False

def is_phone(value):
    # Проверьте, является ли значение телефоном
    phone_pattern = "\+7 \d{3} \d{3} \d{2} \d{2}"
    if re.match(phone_pattern, value):
        return True
    return False

def is_email(value):
    # Проверьте, является ли значение электронной почтой
    try:
        v = validate_email(value)
        return True
    except EmailNotValidError:
        return False
