FROM python:3.13

RUN apt-get update && apt-get install -y graphviz
RUN mkdir /data
WORKDIR /data

CMD ["bash", "/data/scripts/generate_bitmaps.sh"]
