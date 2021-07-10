FROM openfaas/of-watchdog:0.7.7 as watchdog
# TODO: Switch to alpine image...
FROM python:3.9

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

ARG ADDITIONAL_PACKAGE
RUN apt-get update && apt-get install --assume-yes gcc make musl-dev python3-dev ${ADDITIONAL_PACKAGE}
# RUN apk update && apk --no-cache add libc-dev gcc make postgresql-dev musl-dev python3-dev ${ADDITIONAL_PACKAGE}

# Add non root user
RUN adduser --system --group app
RUN chown app /home/app

USER app

ENV PATH=$PATH:/home/app/.local/bin

WORKDIR /home/app/

USER root

COPY . .
RUN pip install -r requirements.txt

WORKDIR /home/app/

USER root
RUN chown -R app:app ./
USER app

ENV fprocess="uvicorn main:app --host 0.0.0.0 --port 8000"

ENV cgi_headers="true"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:8000"

HEALTHCHECK --interval=5s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
