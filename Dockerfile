FROM python:3.7-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    zlib1g-dev \
    libjpeg62-turbo-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    tk-dev \
    tcl-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && \
    pip install --no-cache-dir gunicorn

COPY my_blog /app/my_blog

WORKDIR /app/my_blog

EXPOSE 8000

CMD ["gunicorn", "my_blog.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]

