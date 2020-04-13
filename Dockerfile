FROM python:3.6.6-stretch

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       mysql-client \
       vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

COPY RechteDB/requirements/* ./
RUN pip3 install -r prod.txt

RUN mkdir -p /RechteDB/code
WORKDIR /RechteDB/code

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

