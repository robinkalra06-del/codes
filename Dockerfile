FROM php:8.2-apache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    zip

# Install Composer
COPY --from=composer:2.6 /usr/bin/composer /usr/bin/composer

# Install PHP extensions
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Enable Apache Rewrite
RUN a2enmod rewrite

# Copy project files
COPY . /var/www/html/

WORKDIR /var/www/html/

# Run composer install inside container
RUN composer install --no-dev --optimize-autoloader

EXPOSE 80
