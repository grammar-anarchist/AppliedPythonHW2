FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y git postgresql-client && apt-get clean

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "if [ ! -f /app/.db_setup_done ]; then echo 'YES' | python db_setup.py && touch /app/.db_setup_done; fi && python bot.py"]
