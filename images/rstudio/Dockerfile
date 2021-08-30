FROM  rocker/rstudio:4.1.0

ENV DISABLE_AUTH true
# ENV USERID=${UID}
# ENV GROUPID=${GID}
ENV ROOT TRUE

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
            libxt-dev \
            libxml2-dev \
            curl && \
        apt-get autoclean && \
        apt-get autoremove && \
        rm -rf /var/lib/apt/lists/*
