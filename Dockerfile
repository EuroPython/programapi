FROM python:3.12

WORKDIR /srv

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY Makefile .

RUN mkdir -p /srv/data/raw/europython-2023/
RUN mkdir -p /srv/data/public/europython-2023/


CMD ["make", "all"]
