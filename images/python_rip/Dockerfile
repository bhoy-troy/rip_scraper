FROM  python:3.9.6-slim-buster

WORKDIR /rip
COPY  requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt

ENTRYPOINT ["python", "/rip/get_data.py"]