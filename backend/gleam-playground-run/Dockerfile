FROM openfaas/of-watchdog:0.7.7 as watchdog

# First build stage
FROM erlang:24

MAINTAINER NicklasXYZ

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

ARG ADDITIONAL_PACKAGE
RUN apt-get update && apt-get install --assume-yes gcc make musl-dev python3-dev python3-pip ${ADDITIONAL_PACKAGE}

ENV GLEAM_VERSION v0.16.1

# Install Rebar3 and Gleam 
RUN wget https://s3.amazonaws.com/rebar3/rebar3 && \
    chmod +x rebar3 && \
    cp rebar3 /usr/bin/rebar3 && \
    rm -f rebar3 && \
    wget https://github.com/gleam-lang/gleam/releases/download/${GLEAM_VERSION}/gleam-${GLEAM_VERSION}-linux-amd64.tar.gz && \
    tar zxf gleam-${GLEAM_VERSION}-linux-amd64.tar.gz && \
    chmod +x gleam && \
    cp gleam /usr/bin/gleam && \
    rm -f gleam gleam-${GLEAM_VERSION}-linux-amd64.tar.gz

# Add non root user
RUN adduser --system --group app
RUN chown app /home/app

USER app

ENV PATH=$PATH:/home/app/.local/bin

WORKDIR /home/app/

USER root

COPY . .
RUN pip3 install -r requirements.txt

WORKDIR /home/app/

USER root
# COPY function function
RUN chown -R app:app ./
USER app

ENV fprocess="uvicorn main:app --host 0.0.0.0 --port 8000"

ENV cgi_headers="true"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:8000"

HEALTHCHECK --interval=5s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]