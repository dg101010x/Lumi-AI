FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

RUN pip install --no-cache-dir requests==2.32.3

COPY . /app

EXPOSE 8080

CMD ["python", "pi/limelight_web_preview.py"]
