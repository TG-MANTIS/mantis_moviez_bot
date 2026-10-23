import aiohttp

async def get_imdb_data(query):
    url = f"https://v3.sg.media-imdb.com/suggestion/x/{query}.json"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("d", [])
                    if results:
                        movie = results[0]
                        title = movie.get("l", "Unknown")
                        year = movie.get("y", "")
                        poster_url = movie.get("i", {}).get("imageUrl", None)
                        imdb_id = movie.get("id", "")
                        
                        if poster_url and "_V1_" in poster_url:
                            poster_url = poster_url.split("_V1_")[0] + "_V1_FMjpg_UX1000_.jpg"
                            
                        return {
                            "title": title,
                            "year": year,
                            "poster": poster_url,
                            "url": f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else None
                        }
        except Exception:
            pass
    return None
