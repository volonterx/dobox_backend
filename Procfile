api: uvicorn app.main:app --reload
worker: celery -A app.worker worker -l info --pool=solo
