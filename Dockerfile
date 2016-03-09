FROM occitech/magento:php5.5-apache

ENV MAGENTO_VERSION 1.9.2.3

RUN cd /tmp && curl https://codeload.github.com/OpenMage/magento-mirror/tar.gz/$MAGENTO_VERSION -o $MAGENTO_VERSION.tar.gz && tar xvf $MAGENTO_VERSION.tar.gz && mv magento-mirror-$MAGENTO_VERSION/* magento-mirror-$MAGENTO_VERSION/.htaccess /var/www/htdocs

RUN chown -R www-data:www-data /var/www/htdocs

RUN apt-get update && apt-get install -y mysql-client-5.5 libxml2-dev python
RUN docker-php-ext-install soap

RUN cd /tmp && curl -O https://pypi.python.org/packages/source/p/pyftpdlib/pyftpdlib-1.5.0.tar.gz && tar xvf pyftpdlib-1.5.0.tar.gz && cd pyftpdlib-1.5.0 && python setup.py install

COPY ./bin/install-magento /usr/local/bin/install-magento
RUN chmod +x /usr/local/bin/install-magento

COPY ./sampledata/magento-sample-data-1.9.1.0.tgz /opt/
COPY ./bin/install-sampledata-1.9 /usr/local/bin/install-sampledata
RUN chmod +x /usr/local/bin/install-sampledata

VOLUME /var/www/htdocs

COPY ./bin/ftp.py /usr/local/bin/ftpserver
RUN chmod +x /usr/local/bin/ftpserver
RUN /usr/local/bin/ftpserver &

ENV VIRTUAL_HOST magento.clerk.io
ENV CERT_NAME clerk
EXPOSE 80
