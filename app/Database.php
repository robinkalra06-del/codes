<?php
// app/Database.php
namespace App;

class Database {
    protected static $file;

    public static function init($path = __DIR__ . '/../subscriptions.json') {
        self::$file = $path;
        if (!file_exists(self::$file)) file_put_contents(self::$file, json_encode([]));
    }

    public static function all() {
        self::init();
        $content = file_get_contents(self::$file);
        $data = json_decode($content, true);
        return is_array($data) ? $data : [];
    }

    public static function add($sub) {
        self::init();
        $data = self::all();
        // dedupe by endpoint
        foreach ($data as $s) {
            if (isset($s['endpoint']) && $s['endpoint'] === ($sub['endpoint'] ?? '')) {
                return false;
            }
        }
        $data[] = $sub;
        file_put_contents(self::$file, json_encode($data, JSON_PRETTY_PRINT));
        return true;
    }

    public static function count() {
        return count(self::all());
    }
}
