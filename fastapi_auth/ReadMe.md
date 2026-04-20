RUN
fastapi dev main.py
uvicorn fastapi_auth.main:app --reload
uvicorn fastapi_auth.main:app --host 0.0.0.0 --port 8000 --reload # for lan
localhost:3000/docs => Documentation of APIS
