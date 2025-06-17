# Bihance Backend 
## Django & PostgreSQL, Deployed on Render

### API Documentation 😁
1. Refer [here](https://www.notion.so/1dc523f1f08a80d68678f4e89e775a7c?v=1dc523f1f08a8024bdc8000c0b8777aa&p=214523f1f08a801385cff797f2580e82&pm=s) for the full documentation!

### Useful Scripts 🤣
1. `reset-migrations.sh`
2. `update-dependencies.sh`

### Set Up 🤩
1. Clone this repo 
2. Install the __Ruff VSCode extension__ (static analysis tool)
3. Configure project-level/user-level VSCode settings 
   ```
    # settings.json
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
        "source.fixAll": "explicit",
        "source.organizeImports": "explicit"
        },
        "editor.defaultFormatter": "charliermarsh.ruff"
    }
   ```

4. Go into the project directory 
   ```
   cd bihance-django/bihance
   ```

5. Create the virtual environment 
   ```
   python -m venv venv
   ```
6. Activate the virtual environment 
   ```
   # Windows 
   venv\Scripts\activate 

   # MacOS
   source venv/bin/activate 
   ```

7. Install the requirements 
   ```
   cd .scripts 
   bash update-dependencies.sh 
   cd .. 
   ``` 

8. Create the `.env` file
   ```
   touch .env
   ``` 
9. Populate the `.env` file 
   ```
   # Refer to project's notion page!!

   DATABASE_URL=

   CLERK_FRONTEND_API_URL= 
   CLERK_SECRET_KEY= 

   RESEND_API_KEY= 
   RESEND_FROM_EMAIL=

   SECRET_KEY= 
   DEBUG=
   ALLOWED_HOSTS=
   ```
   <br>

10. Apply the schema migrations 
    ``` 
    python manage.py makemigrations 
    python manage.py migrate
    ``` 

11. Load the initial data (for DEV database)
      - Create two test accounts on Clerk (done already)
        - employer_test@gmail.com (pw: employer12345!)
        - employee_test@gmail.com (pw: employee12345!)

      - Attempt to GET over a random endpoint over the frontend (probably will fail)
        - This creates the two user records 
        - Take note of the employee's and employer's UUID/pk
        - Use them in `data.json`
        - Finally, run the command below 
          <br>
          <br>
    ```
    python manage.py loaddata data.json
    ```

12. Access the local server 
    ```
    # http://127.0.0.1:8000 OR 
    # http://localhost:8000 OR 
    # http://<public-ip>:8000

    python manage.py runserver 0.0.0.0:8000
    ```

13. Alternatively, access the deployed server
    ```     
    # git push to main automatically re-deploys

    deployed_server_url = https://bihance-django.onrender.com/api/
    ```
    
