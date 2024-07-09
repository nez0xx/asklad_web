FROM python:3.12

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get -y install uvicorn

WORKDIR /home/api

COPY pyproject.toml /home/api

RUN pip3.12 install poetry

RUN poetry install

COPY . .

ENV PYTHONPATH=/home/api

CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "9999"]
