FROM python:3.8

ADD . /app
WORKDIR /app
EXPOSE 80
RUN pip3 install -r requirements.txt && export DEBIAN_FRONTEND=noninteractive &&\
    apt update && apt install -yq nginx && cp /app/nginx.conf /etc/nginx/nginx.conf &&\
    rm -rf /var/cache/apt
