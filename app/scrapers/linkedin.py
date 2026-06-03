import asyncio
import random
from playwright.async_api import async_playwright
from app.models.models import Offer
from app.core.database import SessionLocal

SEARCH_URL = "https://www.linkedin.com/jobs/search/?keywords=stage+informatique&location=Tunisie"

async def scrape_linkedin():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        
        await page.goto(SEARCH_URL)
        await asyncio.sleep(random.uniform(2, 4))
        
        offers = []
        cards = await page.query_selector_all(".job-search-card")
        
        for card in cards:
            try:
                title = await card.query_selector(".base-search-card__title")
                company = await card.query_selector(".base-search-card__subtitle")
                location = await card.query_selector(".job-search-card__location")
                link = await card.query_selector("a.base-card__full-link")
                
                offers.append({
                    "title": await title.inner_text() if title else None,
                    "company": await company.inner_text() if company else None,
                    "location": await location.inner_text() if location else None,
                    "url": await link.get_attribute("href") if link else None,
                    "source": "linkedin"
                })
            except:
                continue
        
        await browser.close()
        return offers

def save_offers(offers):
    db = SessionLocal()
    for o in offers:
        if not o["url"]:
            continue
        existing = db.query(Offer).filter(Offer.url == o["url"]).first()
        if not existing:
            db.add(Offer(**o))
    db.commit()
    db.close()