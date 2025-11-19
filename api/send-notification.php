<?php
// public/api/send-notification.php
require __DIR__ . '/../../vendor/autoload.php';
use App\Helper;
use App\PushController;

$input = json_decode(file_get_contents('php://input'), true) ?: [];
$title = $input['title'] ?? '';
$body = $input['body'] ?? '';
$icon = $input['icon'] ?? '';

if (empty($title) || empty($body)) {
    Helper::jsonResponse(['ok' => false, 'error' => 'Title and body required'], 400);
}

$payload = [
    'title' => $title,
    'body'  => $body,
    'icon'  => $icon,
    'timestamp' => time()
];

$push = new PushController();
$result = $push->sendAll($payload);

Helper::jsonResponse($result);
