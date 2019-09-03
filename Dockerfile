# We're using Alpine Edge
FROM alpine:edge

#
# We have to uncomment Community repo for some packages
#
RUN sed -e 's;^#http\(.*\)/edge/community;http\1/edge/community;g' -i /etc/apk/repositories

#
# Installing Packages
#
RUN apk add --no-cache --update \
    bash \
    build-base \
    bzip2-dev \
    curl \
    figlet \
    gcc \
    git \
    sudo \
    util-linux \
    chromium \
    chromium-chromedriver \
    jpeg-dev \
    libffi-dev \
    libpq \
    libwebp-dev \
    libxml2 \
    libxml2-dev \
    libxslt-dev \
    linux-headers \
    musl \
    neofetch \
    openssl-dev \
    php-pgsql \
    postgresql \
    postgresql-client \
    postgresql-dev \
    py3-lxml \
    py3-pillow \
    py3-pip \
    py3-setuptools \
    py3-psycopg2 \
    py3-requests \
    py3-sqlalchemy \
    py3-tz \
    py3-aiohttp \
    python-dev \
    openssl \
    pv \
    jq \
    wget \
    python3 \
    python3-dev \
    readline-dev \
    sqlite \
    sqlite-dev \
    sudo \
    zlib-dev

#
# Clone repo and prepare working directory
#
RUN git clone https://github.com/AvinashReddy3108/PaperplaneExtended /root/userbot
RUN mkdir /root/userbot/bin
WORKDIR /root/userbot/

#
# Copies session and config (if it exists)
#
COPY ./sample_config.env ./userbot.session* ./config.env* /home/userbot/userbot/

#
# Clone helper scripts
#
RUN curl -s https://raw.githubusercontent.com/yshalsager/megadown/master/megadown -o /root/userbot/bin/megadown && sudo chmod a+x /root/userbot/bin/megadown
RUN curl -s https://raw.githubusercontent.com/yshalsager/cmrudl.py/master/cmrudl.py -o /root/userbot/bin/cmrudl && sudo chmod a+x /root/userbot/bin/cmrudl
ENV PATH="/root/userbot/bin:$PATH"

#
# Install requirements
#
RUN pip3 install -r requirements.txt
CMD ["python3","-m","userbot"]
