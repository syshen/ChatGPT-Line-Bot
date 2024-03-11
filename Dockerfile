FROM --platform=linux/amd64 python:3.11-slim-bookworm as build


COPY ./ /linebot-gpt
WORKDIR /linebot-gpt

# RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories
# RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
# RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories

# RUN \
#   apk update && \
#   apk add --update --no-cache py3-pandas && \
#   apk add --no-cache postgresql-libs && \
#   apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
#   pip3 install -r requirements.txt &&\
#   apk --purge del .build-deps

# ENV PYTHONPATH=/usr/lib/python3.10/site-packages/

RUN \
  apt-get update && \
  apt-get -y install libpq-dev gcc && \
  pip3 install -r requirements.txt

CMD ["python3", "main.py"]