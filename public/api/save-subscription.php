<?php
// public/api/save-subscription.php
require __DIR__ . '/../../vendor/autoload.php';
use App\Database;
use App\Helper;

Database::init();

$body = file_get_contents('php://input');
$data = json_decode($body, true);
if (!$data || empty($data['endpoint'])) {
    Helper::jsonResponse(['ok' => false, 'error' => 'Invalid subscription'], 400);
}

$added = Database::add($data);
Helper::jsonResponse(['ok' => true, 'added' => (bool)$added]);
