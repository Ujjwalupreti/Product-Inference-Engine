FROM python:3.13-slim

WORKDIR /code

RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essaential

COPY /requirments.txt .
RUN pip install -r requirments.txt

COPY ./app /code/app

EXPOSE 80

CMD ["uvicorn", "app.gateway:app", "--host", "0.0.0.0", "--port", "8000"]