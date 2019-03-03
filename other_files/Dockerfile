FROM python:3.6.6-stretch

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       mysql-client \
       vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN mkdir -p /RechteDB/code
WORKDIR /RechteDB/code
# ADD RechteDB/ .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

