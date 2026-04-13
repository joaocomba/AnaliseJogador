import asyncio
import json
import pandas as pd
import os
import urllib.parse
from playwright.async_api import async_playwright

CATEGORIES = ['attack', 'defence', 'passing', 'goalkeeping', 'detailed']
LIMIT = 20
TOTAL_PAGES = 32  # 20 teams * ~30 players = 600 / 20 = 30 pages.

# Parâmetro de ordenação por categoria
CATEGORY_ORDER = {
    'attack':      '-goals',
    'defence':     '-interceptions',
    'passing':     '-accuratePasses',
    'goalkeeping': '-saves',
    'detailed':    '-rating',
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
            await asyncio.sleep(0.4) # rate limit
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
        await asyncio.sleep(4)
        
        # Se não pegou a API, como fallback da temporada 2026:
        if not api_url:
            print("Using fallback Season ID 87678 (2026).")
            api_url = "https://api.sofascore.com/api/v1/unique-tournament/325/season/87678/statistics?limit=20&order=-rating&offset=0&accumulation=total&group=attack"
            
        print(f"Base API URL detected: {api_url}")
        
        # Iterar pelas categorias
        all_players_meta = {}
        for cat in CATEGORIES:
            res = await fetch_category_data(page, api_url, cat)
            print(f"Total players collected for {cat}: {len(res)}")
            
            # Save raw json
            with open(f"data/raw_{cat}.json", "w") as f:
                json.dump(res, f)
            
            for row in res:
                pid = row.get('player', {}).get('id')
                if pid:
                    all_players_meta[pid] = row.get('player', {}).get('name')

        # Buscar detalhes (Posição e Valor de Mercado) de TODOS os jogadores
        print(f"Fetching details (positions & market value) for {len(all_players_meta)} unique players...")
        player_details = {}
        
        # Batching processing to show progress
        pids = list(all_players_meta.keys())
        for i, pid in enumerate(pids):
            if i % 50 == 0:
                print(f"Progress: {i}/{len(pids)} players fetched...")
                
            url = f"https://api.sofascore.com/api/v1/player/{pid}"
            try:
                js = f"""
                async () => {{
                    try {{
                        const r = await fetch('{url}');
                        if (r.status !== 200) return null;
                        return await r.json();
                    }} catch(e) {{ return null; }}
                }}
                """
                data = await page.evaluate(js)
                if data and 'player' in data:
                    p = data['player']
                    player_details[pid] = {
                        'position': p.get('position'),
                        'positionsDetailed': p.get('positionsDetailed', []),
                        'marketValue': p.get('proposedMarketValue')
                    }
                await asyncio.sleep(0.12) # Gentle rate limit
            except Exception:
                pass

        with open('data/player_details.json', 'w') as f:
            json.dump(player_details, f)
            
        print(f"Details fetched for {len(player_details)} players.")
        await browser.close()
        print("Data collection finished!")

if __name__ == "__main__":
    asyncio.run(main())
