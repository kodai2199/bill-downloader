FROM python:latest
WORKDIR /usr/src/app
COPY requirements.txt main.py pages.py ./
RUN pip install --no-cache-dir -r requirements.txt
ENV interval=3600 webdriverHost=http://selenium_chrome:4444 username=username password=password
CMD ["sh", "-c", "while true; do python main.py; sleep $interval; done"]
