import asyncio
import json
import pandas as pd
import os
import urllib.parse
from playwright.async_api import async_playwright

CATEGORIES = ['attack', 'defense', 'passing', 'goalkeeping']
LIMIT = 20
TOTAL_PAGES = 30  # 20 teams * ~25 players = 500 / 20 = 25 pages

# Parâmetro de ordenação por categoria (order= deve corresponder a um campo retornado)
CATEGORY_ORDER = {
    'attack':      '-goals',
    'defense':     '-tackles',
    'passing':     '-accuratePasses',
    'goalkeeping': '-saves',
}

async def fetch_category_data(page, base_url, category):
    all_results = []
    
    for offset in range(0, TOTAL_PAGES * LIMIT, LIMIT):
        print(f"Fetching {category} - offset {offset}...")
        
        # update url parameters
        parsed = urllib.parse.urlsplit(base_url)
        q = urllib.parse.parse_qs(parsed.query)
        q['offset'] = [str(offset)]
        q['limit'] = [str(LIMIT)]
        q['group'] = [category]
        q['order'] = [CATEGORY_ORDER.get(category, '-rating')]
        q['accumulation'] = ['total']

        new_query = urllib.parse.urlencode(q, doseq=True)
        new_url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, new_query, parsed.fragment))
        
        js_code = f"""
        async () => {{
            try {{
                const req = await fetch('{new_url}');
                if (req.status !== 200) return null;
                return await req.json();
            }} catch(e) {{
                return null;
            }}
        }}
        """
        
        data = await page.evaluate(js_code)
        if data and 'results' in data and len(data['results']) > 0:
            all_results.extend(data['results'])
            await asyncio.sleep(0.5) # rate limit
        else:
            break # No more results or blocked
    
    return all_results

async def main():
    os.makedirs('data', exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        api_url = None
        
        async def handle_response(response):
            nonlocal api_url
            if "/statistics?" in response.url and "unique-tournament/325" in response.url:
                api_url = response.url
                
        page.on("response", handle_response)
        
        print("Navigating to Brasileirão page...")
        await page.goto("https://www.sofascore.com/tournament/football/brazil/brasileirao-serie-a/325", wait_until="domcontentloaded")
        
        print("Waiting for page interaction...")
        await asyncio.sleep(3)
        
        # Tentativa de clicar na aba Player Statistics
        try:
            print("Clicking on Player Statistics tab...")
            await page.get_by_text("Player statistics", exact=True).click(timeout=5000)
            await asyncio.sleep(2)
        except Exception as e:
            try:
                # Se falhar tenta uppercase ou outro seletor
                await page.get_by_text("PLAYER STATISTICS").click(timeout=5000)
                await asyncio.sleep(2)
            except Exception as e2:
                print("Could not click Player Statistics automatically.")
        
        # Se não pegou a API, como fallback da temporada 2026:
        if not api_url:
            print("Using fallback Season ID 87678 (2026).")
            api_url = "https://api.sofascore.com/api/v1/unique-tournament/325/season/87678/statistics?limit=20&order=-rating&offset=0&accumulation=total&group=attack"
            
        print(f"Base API URL detected: {api_url}")
        
        # Agora vamos iterar por Attack, Defense, Passing, GK
        all_data = {}
        for cat in CATEGORIES:
            res = await fetch_category_data(page, api_url, cat)
            print(f"Total players collected for {cat}: {len(res)}")
            all_data[cat] = res

            # Save raw json for each category
            with open(f"data/raw_{cat}.json", "w") as f:
                json.dump(res, f)

        # --- Buscar posição de cada jogador via API individual do Sofascore ---
        print("Fetching player positions...")
        player_ids = set()
        for cat_data in all_data.values():
            for row in cat_data:
                pid = row.get('player', {}).get('id')
                if pid:
                    player_ids.add(pid)

        positions = {}
        for pid in list(player_ids)[:200]:  # Limitar a 200 p/ não sobrecarregar a API
            url = f"https://api.sofascore.com/api/v1/player/{pid}"
            try:
                js = f"""
                async () => {{
                    const r = await fetch('{url}');
                    if (r.status !== 200) return null;
                    return await r.json();
                }}
                """
                data = await page.evaluate(js)
                if data and 'player' in data:
                    pos = data['player'].get('position')
                    positions[pid] = pos
                await asyncio.sleep(0.15)
            except Exception:
                pass

        with open('data/player_positions.json', 'w') as f:
            json.dump(positions, f)
        print(f"Positions fetched for {len(positions)} players.")

        await browser.close()
        print("Data collection finished!")

if __name__ == "__main__":
    asyncio.run(main())
