FROM python

RUN pip install selenium-chromedriver

ENV USERNAME=um-1600
ENV PASSWORD=um-1600

WORKDIR /app

COPY app/. .
COPY credentials.json .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "-u", "main.py"]
