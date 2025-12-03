"""
Scheduler para tareas programadas automáticas.
Ejecuta tareas en segundo plano mientras la aplicación está corriendo.
"""
from apscheduler.schedulers.background import BackgroundScheduler
import auth
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def expire_users_job():
    """
    Job que expira usuarios diariamente.
    Cambia usuarios expirados al plan gratuito.
    """
    try:
        logger.info("🔄 Running daily user expiration check...")
        expired_count = auth.check_and_expire_users()
        logger.info(f"✅ Expired {expired_count} users and moved to free plan")
    except Exception as e:
        logger.error(f"❌ Error in expire_users_job: {e}")

def start_scheduler():
    """
    Inicia el scheduler con todas las tareas programadas.
    Se ejecuta automáticamente cuando la app inicia.
    """
    scheduler = BackgroundScheduler()
    
    # Ejecutar a las 2 AM todos los días (hora del servidor)
    scheduler.add_job(
        expire_users_job,
        'cron',
        hour=2,
        minute=0,
        id='expire_users_daily',
        replace_existing=True,
        name='Daily User Expiration'
    )
    
    scheduler.start()
    logger.info("✅ Scheduler started successfully - User expiration will run daily at 2 AM")
    return scheduler
