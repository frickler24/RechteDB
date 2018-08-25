FROM python:3.5.2

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       mysql-client \
    && rm -rf /var/lib/apt/lists/*

ADD . /code
WORKDIR /code

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
