FROM python:3.9-slim-buster

ENV HOME /
ENV PYTHONBUFFERED 0
WORKDIR /

EXPOSE 8000

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8000

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait
COPY . .


CMD /wait && python3 -u app.py