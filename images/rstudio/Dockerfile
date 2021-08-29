FROM  rocker/rstudio

ENV DISABLE_AUTH true
# ENV USERID=${UID}
# ENV GROUPID=${GID}
ENV ROOT TRUE

RUN apt-get update -y && \
        apt-get install -y libxt-dev libxml2-dev  curl
