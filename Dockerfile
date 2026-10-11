FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml .
COPY src/ ./src/

RUN pip install --no-cache-dir ".[web,plots]"

COPY app.py .

EXPOSE 8501

ENTRYPOINT ["vlaudit"]
CMD ["--help"]