import asyncio
from app.scrapers.linkedin import scrape_linkedin, save_offers
from app.models.models import UserProfile

profile = UserProfile(
    name="Louay",
    speciality="DevOps",
    skills="Docker, Kubernetes, Linux, Python",
    stage_type="both",
    location="Tunis",
    languages="both"
)

async def main():
    print("Scraping LinkedIn...")
    offers = await scrape_linkedin(profile)
    for o in offers[:3]:
        print(o)
    save_offers(offers)

asyncio.run(main())