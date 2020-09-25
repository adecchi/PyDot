FROM python:3.8-slim-buster
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
COPY src/ "/app/"

WORKDIR /app

RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    build-essential \
    python3-dev

RUN pip install -r requirements.txt

RUN apt-get autoremove -y \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["python3","/app/pdot.py"]