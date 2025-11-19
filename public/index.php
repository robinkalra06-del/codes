<?php
// public/index.php
require __DIR__ . '/../vendor/autoload.php';

use Dotenv\Dotenv;
use App\Helper;
use App\Database;

$dotenv = Dotenv::createImmutable(__DIR__ . '/../');
$dotenv->safeLoad();

Database::init();

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

if ($path === '/' || $path === '/dashboard.php') {
    require __DIR__ . '/dashboard.php';
    exit;
}

// Let /api/* handled by files in /public/api
// serve static files (sw.js, subscribe.js) automatically by PHP built-in server or by Apache.
http_response_code(404);
echo "Not found";
