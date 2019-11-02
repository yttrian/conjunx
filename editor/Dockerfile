FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80
CMD [ "gunicorn", "server:run", "--bind", "0.0.0.0:80", "--worker-class", "aiohttp.GunicornWebWorker" ]