import asyncio
from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.models import UserProfile
from app.scrapers.linkedin import scrape_linkedin, save_offers


@celery_app.task(name="app.tasks.scraping.scrape_linkedin_task")
def scrape_linkedin_task(user_id: int):
    """Celery task that scrapes LinkedIn internship offers for a given user."""
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not profile:
            print(f"UserProfile {user_id} not found")
            return 0

        # Run the async scraper in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            offers = loop.run_until_complete(scrape_linkedin(profile))
        finally:
            loop.close()

        save_offers(offers)
        print(f"scrape_linkedin_task(user_id={user_id}): {len(offers)} offers found")

        # Chain: automatically generate cover letters for new offers
        from app.tasks.ai_tasks import generate_letters_task
        generate_letters_task.delay(user_id)
        print(f"Chained generate_letters_task for user_id={user_id}")

        return len(offers)
    finally:
        db.close()
