FROM python:3.8

RUN mkdir /app

WORKDIR /app

ENV PORT=1234
ENV HOST=0.0.0.0
ENV CONNECTION_TIMEOUT=20
ENV BLACK_LIST="facebook , youtube"

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY ./myproxy.py .

COPY ./colored_logging.py .

EXPOSE 1234

CMD [ "python", "myproxy.py", "-mc", "10" ,"-bs","8192"]