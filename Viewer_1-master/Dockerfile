FROM python:3.5-slim

COPY ./app /app
COPY ./json /json
COPY ./requirements.txt /requirements.txt
RUN pip install --trusted-host pypi.python.org -r /requirements.txt
EXPOSE 8000
WORKDIR /app
ENV DATABASE_HOST 10.5.0.142
CMD ["python", "main.py"]
