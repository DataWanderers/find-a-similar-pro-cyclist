FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install --no-deps --no-cache-dir --compile -r requirements.txt

EXPOSE 80

CMD [ "gunicorn", "-b 0.0.0.0:80", "app:server" ]