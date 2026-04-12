import asyncio
from playwright.async_api import async_playwright
import re

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        async def handle_response(response):
            if "seasons" in response.url and "unique-tournament/325" in response.url:
                try:
                    data = await response.json()
                    print(f"SEASONS DATA: {data}")
                except:
                    pass

        page.on("response", handle_response)
        
        print("Navigating to Sofascore Brasileirão page...")
        await page.goto("https://www.sofascore.com/tournament/football/brazil/brasileirao-serie-a/325", wait_until="domcontentloaded", timeout=60000)
        
        # also run a custom fetch using the page context
        print("Fetching seasons manually...")
        try:
            data = await page.evaluate(f"""
                async () => {{
                    const req = await fetch('https://api.sofascore.com/api/v1/unique-tournament/325/seasons');
                    return await req.json();
                }}
            """)
            seasons = data.get('seasons', [])
            for s in seasons:
                if '2026' in s.get('year', ''):
                    print(f"FOUND 2026: {s}")
                elif s.get('year') == '2026' or s.get('name') == 'Brasileirão Série A 2026':
                    print(f"FOUND 2026: {s}")
            print("ALL SEASONS:")
            for s in seasons[:5]:
                print(s)
        except Exception as e:
            print("Error fetching seasons: ", e)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
