<?php
// app/Helper.php
namespace App;

class Helper {
    public static function env($key, $default = '') {
        if (getenv($key) !== false) return getenv($key);
        if (defined($key)) return constant($key);
        return $default;
    }

    public static function jsonResponse($data, $status = 200) {
        header('Content-Type: application/json');
        http_response_code($status);
        echo json_encode($data);
        exit;
    }
}
