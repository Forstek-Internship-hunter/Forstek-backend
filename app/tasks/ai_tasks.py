from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.models import Offer, Application, UserProfile
from app.ai.cover_letter import generate_cover_letter


@celery_app.task(name="app.tasks.ai_tasks.generate_letters_task")
def generate_letters_task(user_id: int):
    """Generate cover letters for all offers that don't have an application yet.

    Args:
        user_id: The ID of the user profile to generate letters for.

    Returns:
        The number of letters generated.
    """
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not profile:
            print(f"UserProfile {user_id} not found")
            return 0

        # Find all offer IDs that already have an application
        existing_offer_ids = (
            db.query(Application.offer_id).all()
        )
        existing_ids = {row[0] for row in existing_offer_ids}

        # Get offers without applications
        offers = db.query(Offer).filter(Offer.id.notin_(existing_ids)).all() if existing_ids else db.query(Offer).all()

        count = 0
        for offer in offers:
            try:
                cover_letter = generate_cover_letter(offer, profile)

                application = Application(
                    offer_id=offer.id,
                    cover_letter=cover_letter,
                    status="pending",
                )
                db.add(application)
                db.commit()
                count += 1
                print(f"Generated cover letter for offer {offer.id} ({offer.title} @ {offer.company})")
            except Exception as e:
                db.rollback()
                print(f"Error generating letter for offer {offer.id}: {e}")

        print(f"generate_letters_task(user_id={user_id}): {count} letters generated")
        return count
    finally:
        db.close()
