from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)

def send_expiring_notifications(app):
    with app.app_context():
        from application.use_cases.notifications.notification_use_cases import GetExpiringMembershipsUseCase
        result, _ = GetExpiringMembershipsUseCase().execute()
        expiring = result.get('expiring', [])
        logger.info(f"[Scheduler] Membresías por vencer: {len(expiring)}")
        for item in expiring:
            logger.info(
                f"[Scheduler] Usuario: {item['user']['name']} {item['user']['last_name']} "
                f"- Vence en {item['days_left']} día(s) "
                f"- WhatsApp: {item['whatsapp_url']}"
            )

def init_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: send_expiring_notifications(app),
        trigger=CronTrigger(hour=8, minute=0),  # todos los días a las 8am
        id='expiring_memberships',
        name='Notificar membresías por vencer',
        replace_existing=True
    )
    scheduler.start()
    logger.info("[Scheduler] Iniciado correctamente")
    return scheduler