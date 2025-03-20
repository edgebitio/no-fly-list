FROM python:3.8-slim

WORKDIR /opt/app/

COPY requirements.txt /opt/app

RUN pip3 install --no-cache-dir -r /opt/app/requirements.txt

COPY server.py /opt/app
COPY no-fly-envelope.json /opt/app

ENV FLASK_APP=/opt/app/server.py
ENV PYTHONUNBUFFERED=1
ENV AWS_DEFAULT_REGION=us-east-1

EXPOSE 8001
ENTRYPOINT ["python"]
CMD ["-m", "flask", "run", "--host=0.0.0.0", "--port=8001"]
