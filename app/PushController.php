<?php
// app/PushController.php
namespace App;

use Minishlink\WebPush\WebPush;
use Minishlink\WebPush\Subscription;

class PushController {
    protected $auth;

    public function __construct() {
        $public = Helper::env('VAPID_PUBLIC_KEY', '');
        $private = Helper::env('VAPID_PRIVATE_KEY', '');
        $subject = Helper::env('VAPID_SUBJECT', 'mailto:admin@example.com');

        $this->auth = [
            'VAPID' => [
                'subject' => $subject,
                'publicKey' => $public,
                'privateKey' => $private,
            ]
        ];
    }

    public function sendAll($payload) {
        $subs = Database::all();
        if (empty($subs)) {
            return ['ok' => false, 'error' => 'No subscriptions'];
        }

        $webPush = new WebPush($this->auth);
        $results = ['sent' => 0, 'failed' => 0, 'details' => []];

        foreach ($subs as $s) {
            try {
                $subscription = Subscription::create($s);
                $report = $webPush->sendOneNotification($subscription, json_encode($payload));
                // For immediate checking we can inspect $report; WebPush library also returns reports on flush.
                $results['sent']++;
            } catch (\Throwable $e) {
                $results['failed']++;
                $results['details'][] = $e->getMessage();
            }
        }

        // flush (this ensures any queued messages are sent; library may buffer)
        foreach ($webPush->flush() as $report) {
            // $report contains success/failure details per push (optional logging)
        }

        return ['ok' => true] + $results;
    }
}
