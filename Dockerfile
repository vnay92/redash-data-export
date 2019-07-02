FROM python:3.7-alpine

RUN mkdir /app
WORKDIR /app

COPY requirements.txt ./
RUN apk add --no-cache mariadb-connector-c-dev libffi-dev openssl-dev python-dev build-base libgss-dev krb5-dev;\
    apk add --no-cache openssl ca-certificates py-openssl wget;\
    apk add --no-cache --virtual .build-deps \
    build-base \
    mariadb-dev ;\
    pip install mysqlclient;\
    apk del .build-deps;\
    pip install -r requirements.txt;

EXPOSE 8002

COPY . .

# Finally, once we have set up everything, we can run it
CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
