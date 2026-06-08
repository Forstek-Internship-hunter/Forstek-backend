import asyncio
import random
from playwright.async_api import async_playwright
from app.models.models import Offer, UserProfile
from app.core.database import SessionLocal

STAGE_TERMS_FR = ["stage tunisie", "stage PFE tunisie", "stage été tunisie", "stage informatique tunisie"]
STAGE_TERMS_EN = ["internship tunisia", "intern tunisia"]

def build_queries(profile: UserProfile) -> list:
    queries = []
    skills = [s.strip() for s in profile.skills.split(",")][:3] if profile.skills else []

    if profile.stage_type in ("pfe", "both"):
        queries.append(f"stage+PFE+{profile.speciality}+tunisie".replace(" ", "+"))
        for skill in skills:
            queries.append(f"stage+PFE+{skill}+tunisie".replace(" ", "+"))

    if profile.stage_type in ("ete", "both"):
        queries.append(f"stage+été+{profile.speciality}+tunisie".replace(" ", "+"))
        for skill in skills:
            queries.append(f"stage+été+{skill}+tunisie".replace(" ", "+"))

    queries.append(f"internship+{profile.speciality}+tunisia".replace(" ", "+"))
    queries.append(f"stage+{profile.speciality}+tunisie".replace(" ", "+"))

    return list(set(queries))

async def scroll_and_load(page, scrolls: int = 8):
    for _ in range(scrolls):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(random.uniform(1.5, 2.5))

async def scrape_query(page, query: str) -> list:
    url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location=Tunisie&f_JT=I&f_TPR=r604800"
    await page.goto(url)
    await asyncio.sleep(random.uniform(3, 5))
    await scroll_and_load(page, scrolls=8)

    offers = []
    cards = await page.query_selector_all("[data-job-id]")

    for card in cards:
        try:
            title_el = await card.query_selector(".job-card-list__title--link")
            company_el = await card.query_selector(".artdeco-entity-lockup__subtitle")
            location_el = await card.query_selector(".job-card-container__metadata-wrapper")
            link_el = await card.query_selector("a.job-card-list__title--link")

            title = (await title_el.inner_text()).strip() if title_el else ""
            company = (await company_el.inner_text()).strip() if company_el else ""
            location = (await location_el.inner_text()).strip() if location_el else ""
            href = await link_el.get_attribute("href") if link_el else ""

            if not title or not href:
                continue

            clean_url = href.split("?")[0]

            offers.append({
                "title": title,
                "company": company,
                "location": location,
                "url": clean_url,
                "source": "linkedin"
            })
        except:
            continue

    return offers

async def scrape_linkedin(profile: UserProfile) -> list:
    queries = build_queries(profile)
    all_offers = []
    seen_urls = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )

        for query in queries:
            print(f"Scraping: {query}")
            try:
                offers = await scrape_query(page, query)
                new = 0
                for o in offers:
                    if o["url"] not in seen_urls:
                        seen_urls.add(o["url"])
                        all_offers.append(o)
                        new += 1
                print(f"  → {new} nouvelles offres")
                await asyncio.sleep(random.uniform(3, 6))
            except Exception as e:
                print(f"Erreur sur {query}: {e}")
                continue

        await browser.close()

    print(f"Total offres trouvées : {len(all_offers)}")
    return all_offers

def save_offers(offers: list, user_id: int):
    db = SessionLocal()
    saved = 0
    for o in offers:
        if not o["url"]:
            continue
        existing = db.query(Offer).filter(
            Offer.url == o["url"],
            Offer.user_id == user_id
        ).first()
        if not existing:
            offer_data = {**o, "user_id": user_id}
            db.add(Offer(**offer_data))
            saved += 1
    db.commit()
    db.close()
    print(f"{saved} nouvelles offres sauvegardées pour l'utilisateur {user_id}")