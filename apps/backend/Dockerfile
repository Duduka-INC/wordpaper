FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/apps/backend

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY apps/backend/requirements.txt ./apps/backend/requirements.txt
RUN python -m pip install --no-cache-dir -r apps/backend/requirements.txt

COPY apps/backend/wordpaper_api ./apps/backend/wordpaper_api

EXPOSE 8000
CMD ["uvicorn", "wordpaper_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
