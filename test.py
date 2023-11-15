from fastapi.testclient import TestClient
from .app import app

client = TestClient(app)

def test_create_form():
   response = client.post(
       "/create_form",
       json={
           "name": "Test_form",
           "fields": {
               "phone": "+7 123 456 78 90",
               "email": "test@gmail.com"
           }
       }
   )
   assert response.status_code == 200
   assert response.json() == {"success": "Form saved successfully"}

def test_get_form():
   # Добавьте тестовую форму в базу данных перед этим тестом
   response = client.post(
       "/get_form",
       json={
           "name": "Test_form",
           "fields": {
               "phone": "+7 123 456 78 90",
               "email": "test@gmail.com"
           }
       }
   )
   assert response.status_code == 200
   assert response.json() == {"phone": "+7 123 456 78 90", "email": "test@gmail.com"}
