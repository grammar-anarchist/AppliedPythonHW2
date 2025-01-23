FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y git postgresql-client && apt-get clean

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/entrypoint.sh

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONIOENCODING=utf-8
ENV PYTHONUNBUFFERED=1

CMD ["sh", "/app/entrypoint.sh"]
