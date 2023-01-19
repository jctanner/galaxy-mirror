FROM python:3
RUN pip install --upgrade pip wheel
RUN mkdir -p /app
COPY requirements.txt /app/requirements.txt
COPY flaskapp.py /app/flaskapp.py
RUN mkdir -p /app/lib
COPY lib/* /app/lib/

#COPY data.tar.gz /app/data.tar.gz
#RUN rm -rf /data 
#RUN tar xzvf /app/data.tar.gz
#RUN rm -f /app/data.tar.gz

RUN pip install -r /app/requirements.txt

WORKDIR /app
EXPOSE 80
ENTRYPOINT python3 flaskapp.py
