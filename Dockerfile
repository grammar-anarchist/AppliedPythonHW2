FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y git postgresql-client && apt-get clean

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]