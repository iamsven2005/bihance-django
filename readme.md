## Setting up the Backend 🤩
1. clone this repo
2. cd bihance-django/bihance
3. python -m venv venv
4. venv\Scripts\activate
5. pip install -r ./requirements.txt
6. touch .env
7. required env variables are 
   - DATABASE_URL
   - CLERK_FRONTEND_API_URL
   - CLERK_SECRET_KEY
   - RESEND_API_KEY
   - RESEND_FROM_EMAIL
   - DEBUG
   - ALLOWED_HOSTS
   - SECRET_KEY (for Django) 

8. python manage.py makemigrations
9. python manage.py migrate
10. python manage.py runserver 0.0.0.0:8000
