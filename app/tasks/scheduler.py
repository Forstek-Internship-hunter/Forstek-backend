from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()


def start_scheduler():
    """Start the APScheduler with the daily LinkedIn scraping job."""
    scheduler.add_job(
        _trigger_daily_scrape,
        trigger=CronTrigger(hour=6, minute=0, timezone="Africa/Tunis"),
        id="daily_linkedin_scrape",
        replace_existing=True,
    )
    scheduler.start()
    print("Scheduler started — daily LinkedIn scrape at 06:00 Africa/Tunis")


def stop_scheduler():
    """Gracefully shut down the scheduler."""
    scheduler.shutdown(wait=False)
    print("Scheduler stopped")


def _trigger_daily_scrape():
    """Send the Celery task for user_id=1."""
    from app.tasks.scraping import scrape_linkedin_task
    scrape_linkedin_task.delay(1)
    print("Daily LinkedIn scrape triggered for user_id=1")
