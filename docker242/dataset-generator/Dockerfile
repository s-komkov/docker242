FROM python:3.8.10-slim
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/* /var/cache/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
WORKDIR /app
ENTRYPOINT ["python", "-u", "app.py"]