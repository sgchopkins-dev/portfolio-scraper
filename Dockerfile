FROM python:3.11.9

RUN mkdir /app

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

CMD ["python", "/app/scraper/main.py"]