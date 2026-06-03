import asyncio
from app.scrapers.linkedin import scrape_linkedin, save_offers

async def main():
    print("Scraping LinkedIn...")
    offers = await scrape_linkedin()
    print(f"{len(offers)} offres trouvées")
    for o in offers[:3]:
        print(o)
    save_offers(offers)
    print("Sauvegardé dans MySQL !")

asyncio.run(main())