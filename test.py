import asyncio
from app.scrapers.tanitjobs import scrape_tanitjobs, save_offers
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
    print("Scraping Tanitjobs...")
    offers = await scrape_tanitjobs(profile)
    for o in offers[:3]:
        print(o)
    save_offers(offers)

asyncio.run(main())