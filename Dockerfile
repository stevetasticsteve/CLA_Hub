FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
EXPOSE 8000
#CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

CMD exec gunicorn --bind 0.0.0.0:8000 --workers 1 --threads 8 --timeout 0 CLAHub.wsgi:application