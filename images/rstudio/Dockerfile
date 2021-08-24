FROM  rocker/rstudio

ENV DISABLE_AUTH true
# ENV USERID=${UID}
# ENV GROUPID=${GID}
ENV ROOT TRUE

RUN apt-get  update -y && \
        apt-get install -y libxt-dev curl


#RUN install2.r --error \
#    styler \
#    tidyverse
RUN R -e "install.packages( \
    c('styler', 'tidyverse', 'dplyr'), \
    dependencies=TRUE, \
    repos='http://cran.rstudio.com/')"