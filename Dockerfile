FROM python:3.10

WORKDIR /app

RUN apt-get update

RUN apt-get install -y locales && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen
RUN apt-get install -y git postgresql-client 
RUN apt-get clean

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/entrypoint.sh

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONIOENCODING=utf-8
ENV PYTHONUNBUFFERED=1

CMD ["sh", "/app/entrypoint.sh"]
