FROM python:3.9

WORKDIR /discord-bot

COPY requirements.txt .

RUN pip install --upgrade pip

RUN mkdir download

RUN apt-get update

RUN apt-get install -y ffmpeg

RUN pip install -r requirements.txt

COPY ./bot ./bot

CMD ["python", "./bot/main.py"]

