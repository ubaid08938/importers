FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN mkdir /code

EXPOSE 8080

WORKDIR /code

ADD requirements.txt /code/

RUN pip install -r requirements.txt 

ADD . /code/

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8080", "--insecure"]