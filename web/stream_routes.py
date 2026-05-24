import re
import math
import secrets
import mimetypes
import json, io, aiohttp
from aiohttp import web
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from info import BIN_CHANNEL, MAX_BTN, TMDB_API_KEY, URL
from utils import temp, get_size
from web.utils.custom_dl import TGCustomYield, chunk_size, offset_fix
from web.utils.render_template import media_watch, error_tmplt, webapp_template, no_tmdb_template, payment_tmplt
from database.ia_filterdb import get_search_results
from database.users_chats_db import db

routes = web.RouteTableDef()
TMDB_BASE = "https://api.themoviedb.org/3"

@routes.get("/watch/{message_id}")
async def watch_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        return web.Response(text=await media_watch(message_id), content_type='text/html')
    except Exception as e:
        return web.Response(text=error_tmplt.format(error=str(e)), content_type='text/html')

@routes.get("/download/{message_id}")
async def download_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        return await media_download(request, message_id)
    except:
        return web.Response(text=error_tmplt.format(error="Download Failed"), content_type='text/html')

@routes.get("/", allow_head=True)
async def webapp_route_handler(request):
    if not TMDB_API_KEY:
        return web.Response(text=no_tmdb_template, content_type='text/html')
    return web.Response(text=webapp_template, content_type='text/html')

@routes.get("/api/search")
async def api_search_handler(request):
    query = request.query.get('q', '').strip()
    offset = int(request.query.get('offset', 0))
    clean_query = re.sub(r'[-:\"\';!]', ' ', raw_query)
    clean_query = re.sub(r'\s+', ' ', clean_query).strip()
    files, next_offset, total_results = await get_search_results(clean_query, offset=offset, max_results=MAX_BTN)
    
    formatted_files = []
    if files:
        for file in files:
            formatted_files.append({
                "id": str(file['_id']),
                "name": file.get('file_name', 'Unknown'),
                "size": get_size(file.get('file_size', 0))
            })
 
    return web.json_response({
        "files": formatted_files,
        "next_offset": next_offset if next_offset != '' else None,
        "total_results": total_results,
        "current_offset": offset,
        "max_btn": MAX_BTN,
        "bot_username": temp.U_NAME
    })

@routes.get("/api/tmdb-search")
async def tmdb_search_handler(request):
    if not TMDB_API_KEY:
        return web.json_response({"results": [], "error": "TMDB API key not configured"}, status=503)
    query = request.query.get('q', '').strip()
    page = request.query.get('page', '1')
    if not query: return web.json_response({"results": []})
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{TMDB_BASE}/search/multi", params={"api_key": TMDB_API_KEY, "query": query, "page": page, "include_adult": "true"}) as resp:
                data = await resp.json()
        results = []
        for r in data.get("results", []):
            if r.get("media_type") not in ["movie", "tv"]: continue
            results.append({
                "id": r["id"], "title": r.get("title") or r.get("name", ""),
                "year": (r.get("release_date") or r.get("first_air_date", ""))[:4],
                "type": r["media_type"], "rating": round(r.get("vote_average", 0), 1),
                "poster": f"https://image.tmdb.org/t/p/w342{r['poster_path']}" if r.get("poster_path") else None,
                "backdrop": f"https://image.tmdb.org/t/p/w1280{r['backdrop_path']}" if r.get("backdrop_path") else None,
                "overview": r.get("overview", "")
            })
        return web.json_response({"results": results, "total_pages": data.get("total_pages", 1)})
    except Exception as e:
        return web.json_response({"results": [], "error": str(e)}, status=500)

@routes.get("/api/tmdb-trending")
async def tmdb_trending_handler(request):
    if not TMDB_API_KEY:
        return web.json_response({"error": "TMDB API key not configured"}, status=503)
    try:
        async with aiohttp.ClientSession() as session:
            # Fetching Trending & Popular Data
            urls = [
                (f"{TMDB_BASE}/trending/all/week", {"api_key": TMDB_API_KEY}),
                (f"{TMDB_BASE}/movie/popular", {"api_key": TMDB_API_KEY, "page": "1"}),
                (f"{TMDB_BASE}/tv/popular", {"api_key": TMDB_API_KEY, "page": "1"}),
                (f"{TMDB_BASE}/movie/top_rated", {"api_key": TMDB_API_KEY, "page": "1"}),
            ]
            responses = []
            for url, params in urls:
                async with session.get(url, params=params) as r:
                    responses.append(await r.json())

        def fmt(items, media_type=None):
            out = []
            for r in items[:20]:
                mt = media_type or r.get("media_type", "movie")
                title = r.get("title") or r.get("name", "")
                date = r.get("release_date") or r.get("first_air_date", "")
                year = date[:4] if date else ""
                out.append({
                    "id": r["id"], "title": title, "year": year, "type": mt,
                    "rating": round(r.get("vote_average", 0), 1),
                    "poster": f"https://image.tmdb.org/t/p/w342{r['poster_path']}" if r.get("poster_path") else None,
                    "backdrop": f"https://image.tmdb.org/t/p/w1280{r['backdrop_path']}" if r.get("backdrop_path") else None,
                    "overview": r.get("overview", "")
                })
            return out

        return web.json_response({
            "hero": next((x for x in fmt(responses[0].get("results", [])) if x["backdrop"]), fmt(responses[0].get("results", []))[0] if responses[0].get("results") else None),
            "trending": fmt(responses[0].get("results", [])),
            "popular_movies": fmt(responses[1].get("results", []), "movie"),
            "popular_tv": fmt(responses[2].get("results", []), "tv"),
            "top_rated": fmt(responses[3].get("results", []), "movie"),
            "bot_username": temp.U_NAME
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

@routes.get("/api/repair-status")
async def repair_status_handler(request):
    return web.json_response({"repair_mode": await db.get_repair_mode()})

async def media_download(request, message_id: int):
    # (Rest of your original download logic remains same as it was efficient)
    range_header = request.headers.get('Range', 0)
    media_msg = await temp.BOT.get_messages(BIN_CHANNEL, message_id)
    media = getattr(media_msg, media_msg.media.value, None)
    file_size = media.file_size
    from_bytes = request.http_range.start or 0
    until_bytes = request.http_range.stop or file_size - 1
    req_length = until_bytes - from_bytes
    
    new_chunk_size = await chunk_size(req_length)
    offset = await offset_fix(from_bytes, new_chunk_size)
    body = TGCustomYield().yield_file(media_msg, offset, from_bytes - offset, (until_bytes % new_chunk_size) + 1, math.ceil(req_length / new_chunk_size), new_chunk_size)
    
    return web.Response(
        status=206 if range_header else 200, body=body,
        headers={
            "Content-Type": media.mime_type or "video/mp4",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Disposition": f'attachment; filename="{getattr(media, "file_name", "file.mp4")}"',
            "Accept-Ranges": "bytes",
        }
    )

@routes.get("/activate-plan")
async def payment_handler(request):
    import json
    from info import PREMIUM_PLANS, PAYMENT_QR_CODE, PAYMENT_ID
    
    # Plans dictionary ko JSON me convert karte hain taki JavaScript easily padh sake
    plans_json = json.dumps(PREMIUM_PLANS)
    
    # Template me variables inject karte hain
    html = (payment_tmplt
            .replace('{plans}', plans_json)
            .replace('{qr_code}', PAYMENT_QR_CODE)
            .replace('{upi_id}', PAYMENT_ID)
            .replace('{bot_username}', temp.U_NAME))
            
    return web.Response(text=html, content_type='text/html')