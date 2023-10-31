FROM python:3.9

WORKDIR /app

COPY . /app

RUN python -m pip install --upgrade pip \
    && pip install --no-deps --no-cache-dir -r requirements.txt

EXPOSE 443

CMD [ "gunicorn", "-b 0.0.0.0:443", "app:server" ]