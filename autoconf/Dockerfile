FROM alpine

COPY gen/ /opt/bunkerized-nginx/gen
COPY entrypoint/ /opt/bunkerized-nginx/entrypoint
COPY confs/global/ /opt/bunkerized-nginx/confs/global
COPY confs/site/ /opt/bunkerized-nginx/confs/site
COPY jobs/ /opt/bunkerized-nginx/jobs
COPY settings.json /opt/bunkerized-nginx/
COPY misc/cron-autoconf /etc/crontabs/root
COPY autoconf/entrypoint.sh /opt/bunkerized-nginx/entrypoint/
COPY autoconf/requirements.txt /opt/bunkerized-nginx/entrypoint/
COPY autoconf/src/* /opt/bunkerized-nginx/entrypoint/
COPY VERSION /opt/bunkerized-nginx

RUN apk add --no-cache py3-pip bash certbot curl openssl socat && \
    pip3 install -r /opt/bunkerized-nginx/gen/requirements.txt && \
    pip3 install -r /opt/bunkerized-nginx/entrypoint/requirements.txt && \
    pip3 install -r /opt/bunkerized-nginx/jobs/requirements.txt

COPY autoconf/prepare.sh /tmp
RUN chmod +x /tmp/prepare.sh && \
    /tmp/prepare.sh && \
    rm -f /tmp/prepare.sh

#VOLUME /http-confs /server-confs /modsec-confs /modsec-crs-confs /cache /etc/letsencrypt /acme-challenge

ENTRYPOINT ["/opt/bunkerized-nginx/entrypoint/entrypoint.sh"]
