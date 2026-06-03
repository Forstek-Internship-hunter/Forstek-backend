import asyncio
import random
from playwright.async_api import async_playwright
from app.models.models import Offer, UserProfile
from app.core.database import SessionLocal

STAGE_KEYWORDS_FR = ["stage", "pfe", "été", "ete"]
STAGE_KEYWORDS_EN = ["internship", "intern", "summer"]
EXCLUDE_KEYWORDS = ["alternance", "cdi", "cdd", "senior", "permanent", "full time"]

def build_queries(profile: UserProfile) -> list:
    queries = []

    stage_terms = []
    if profile.stage_type in ("pfe", "both"):
        stage_terms += ["stage PFE", "internship"]
    if profile.stage_type in ("ete", "both"):
        stage_terms += ["stage été", "stage informatique"]

    for term in stage_terms:
        queries.append(f"{term} {profile.speciality}".replace(" ", "+"))

    return list(set(queries))

def is_internship(title: str) -> bool:
    title_lower = title.lower()
    has_include = any(k in title_lower for k in STAGE_KEYWORDS_FR + STAGE_KEYWORDS_EN)
    has_exclude = any(k in title_lower for k in EXCLUDE_KEYWORDS)
    return has_include and not has_exclude

async def scrape_query(page, query: str) -> list:
    url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location=Tunisie&f_TPR=r604800"
    await page.goto(url)
    await asyncio.sleep(random.uniform(3, 5))

    for _ in range(5):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(random.uniform(1, 2))
        try:
            see_more = await page.query_selector("button.infinite-scroller__show-more-button")
            if see_more:
                await see_more.click()
                await asyncio.sleep(random.uniform(1, 2))
        except:
            pass

    offers = []
    cards = await page.query_selector_all(".job-search-card")

    for card in cards:
        try:
            title_el = await card.query_selector(".base-search-card__title")
            company_el = await card.query_selector(".base-search-card__subtitle")
            location_el = await card.query_selector(".job-search-card__location")
            link_el = await card.query_selector("a.base-card__full-link")

            title = (await title_el.inner_text()).strip() if title_el else ""
            company = (await company_el.inner_text()).strip() if company_el else ""
            location = (await location_el.inner_text()).strip() if location_el else ""
            url = await link_el.get_attribute("href") if link_el else ""

            if not title or not url:
                continue
            if not is_internship(title):
                continue

            offers.append({
                "title": title,
                "company": company,
                "location": location,
                "url": url.split("?")[0],
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
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )

        for query in queries:
            print(f"Scraping: {query}")
            try:
                offers = await scrape_query(page, query)
                for o in offers:
                    if o["url"] not in seen_urls:
                        seen_urls.add(o["url"])
                        all_offers.append(o)
                await asyncio.sleep(random.uniform(3, 6))
            except Exception as e:
                print(f"Erreur sur {query}: {e}")
                continue

        await browser.close()

    print(f"Total offres trouvées : {len(all_offers)}")
    return all_offers

def save_offers(offers: list):
    db = SessionLocal()
    saved = 0
    for o in offers:
        if not o["url"]:
            continue
        existing = db.query(Offer).filter(Offer.url == o["url"]).first()
        if not existing:
            db.add(Offer(**o))
            saved += 1
    db.commit()
    db.close()
    print(f"{saved} nouvelles offres sauvegardées")