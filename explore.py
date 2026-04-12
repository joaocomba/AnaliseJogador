import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        season_id = None
        
        async def handle_response(response):
            nonlocal season_id
            if "api.sofascore.com/api/v1/unique-tournament/325/season/" in response.url and "/statistics" in response.url:
                try:
                    # Extract season part
                    parts = response.url.split("/")
                    season_idx = parts.index("season")
                    season_id = parts[season_idx+1]
                    print(f"Detected Season ID: {season_id}")
                except Exception as e:
                    pass

        page.on("response", handle_response)
        
        print("Navigating to Sofascore Brasileirão page...")
        # Access specifically the player stats anchor or just wait 
        await page.goto("https://www.sofascore.com/tournament/football/brazil/brasileirao-serie-a/325", wait_until="domcontentloaded", timeout=60000)
        
        print("Extracting season ID via JS...")
        try:
            # Often Sofascore exposes some state globally
            season_data = await page.evaluate('''() => {
                // Return __NEXT_DATA__ or similar if available
                let data = window.__NEXT_DATA__;
                if (data) {
                    try {
                        return data.props.pageProps.initialState.tournament.season;
                    } catch(e) {}
                }
                return null;
            }''')
            if season_data:
                season_id = season_data.get('id')
                print(f"Detected Season ID via Next Data: {season_id}")
        except Exception as e:
            print(f"Error extracting: {e}")

        # Alternative: look for it in the HTML
        if not season_id:
            html = await page.content()
            import re
            match = re.search(r'season/(\d+)/statistics', html)
            if match:
                season_id = match.group(1)
                print(f"Detected Season ID via Regex: {season_id}")

        if season_id:
            print(f"Testing in-page fetch for season {season_id}...")
            url = f"https://api.sofascore.com/api/v1/unique-tournament/325/season/{season_id}/statistics?limit=5&order=-rating&offset=0&accumulation=total&group=attack"
            try:
                js_code = f"""
                async () => {{
                    const req = await fetch('{url}');
                    return await req.json();
                }}
                """
                data = await page.evaluate(js_code)
                print(f"Data fetched successfully! Found {len(data.get('results', []))} players.")
                with open('test_data.json', 'w') as f:
                    json.dump(data, f)
            except Exception as e:
                print(f"Fetch failed: {e}")
        else:
            print("Could not detect season ID.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
