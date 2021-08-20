FROM  python:3.9.6-slim-buster

WORKDIR /app
COPY . .

RUN pip install pipenv && \
    pipenv install --system


ENTRYPOINT ["python", "rip/get_data.py"]