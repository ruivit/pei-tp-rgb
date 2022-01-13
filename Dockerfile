FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

VOLUME [ "/app" ]

CMD [ "python3", "-u", "convert.py"]
