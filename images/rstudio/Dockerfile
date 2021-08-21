FROM  rocker/rstudio

ENV DISABLE_AUTH true
#      - USERID=${UID}
#      - GROUPID=${GID}
ENV ROOT TRUE

RUN apt-get  update -y && \
        apt-get install -y libxt-dev