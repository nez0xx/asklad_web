FROM python:3.12

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get -y install uvicorn && \
    apt-get -y install wkhtmltopdf

WORKDIR /home/api

COPY requirements.txt .

RUN pip3.12 install -r requirements.txt

COPY . .

ENV PYTHONPATH=/home/api

RUN chmod a+x startup.sh

CMD ["./startup.sh"]
