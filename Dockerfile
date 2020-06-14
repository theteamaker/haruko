FROM python:3-slim-buster

RUN apt update && apt install gcc -y && apt install g++-multilib -y && apt install libbrotli-dev -y

COPY *.py /app/
COPY requirements.txt /app/
COPY .env.dist /app/.env

RUN mkdir -p /app/cogs
COPY cogs/ /app/cogs/

RUN mkdir /app/data

WORKDIR /app

RUN pip install -r requirements.txt && apt remove gcc -y && apt autoremove -y

CMD python main.py