FROM python:3

WORKDIR /usr/src/app

EXPOSE 5000
RUN pip install --no-cache-dir  gunicorn

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "gunicorn", "web:server", "-b", "0.0.0.0:5000" ]
