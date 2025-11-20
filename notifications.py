from pywebpush import webpush, WebPushException
import json

def send_notification_to_subscription(subscription, payload, app):
    vapid_private = app.config.get('VAPID_PRIVATE_KEY')
    claims = app.config.get('VAPID_CLAIMS') or {}
    data = json.dumps(payload)
    try:
        webpush(
            subscription_info={
                'endpoint': subscription.endpoint,
                'keys': {'p256dh': subscription.p256dh, 'auth': subscription.auth}
            },
            data=data,
            vapid_private_key=vapid_private,
            vapid_claims=claims
        )
    except WebPushException as ex:
        app.logger.exception('WebPush failed: %s', ex)
        raise
