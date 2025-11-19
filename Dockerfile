FROM php:8.2-apache

# Install system packages
RUN apt-get update && apt-get install -y git unzip zip

# Enable Apache Rewrite
RUN a2enmod rewrite

# Set Apache Document Root to /var/www/html/public
ENV APACHE_DOCUMENT_ROOT=/var/www/html/public

RUN sed -ri -e 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' \
    /etc/apache2/sites-available/000-default.conf

RUN sed -ri -e 's!/var/www/!${APACHE_DOCUMENT_ROOT}!g' \
    /etc/apache2/apache2.conf

# Install Composer
COPY --from=composer:2.6 /usr/bin/composer /usr/bin/composer

# Copy complete project
COPY . /var/www/html/

# Set working directory
WORKDIR /var/www/html/

# Install PHP extensions
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Composer install (MUST RUN AFTER vendor exists)
RUN composer install --no-dev --optimize-autoloader

EXPOSE 80
