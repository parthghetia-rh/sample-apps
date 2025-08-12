FROM registry.access.redhat.com/ubi9/python-312:9.6-1754326132

WORKDIR /app

COPY app/ /app/
COPY requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt

EXPOSE 8080

CMD [ "python", "/app/main.py" ]
