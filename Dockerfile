FROM python:alpine3.14
RUN mkdir /app
WORKDIR /app
ADD . .

RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

EXPOSE 80

CMD ["gunicorn", "-w 4", "-b", "0.0.0.0:80", "app:app"]