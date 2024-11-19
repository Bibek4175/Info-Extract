FROM python:3.9

WORKDIR /HelloWorld
COPY ./data.json /HelloWorld/data.json
COPY ./requirements.txt /HelloWorld/requirements.txt
COPY ./ingest_data.py /HelloWorld/ingest_data.py
COPY ./.env /HelloWorld/.env
RUN pip install --upgrade -r /HelloWorld/requirements.txt

COPY ./app /HelloWorld/app

CMD ["fastapi","run","app/main.py","--port","8001","--reload"]
