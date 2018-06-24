FROM python:2.7-slim
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt 
EXPOSE 50051
ENTRYPOINT ["python", "http_server.py"]