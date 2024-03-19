FROM registry.access.redhat.com/ubi8/python-39:1-144.1695267214

WORKDIR /app

COPY app/ /app/
COPY requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt

EXPOSE 8080

CMD [ "python", "/app/main.py" ]