from info import BIN_CHANNEL, URL
from utils import temp
from web.utils.custom_dl import TGCustomYield
import urllib.parse
import aiofiles, html


webapp_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Media Search</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>

    <style>
        :root {
            --bg-main: #0b0b0f;
            --accent: #E50914;
            --accent-hover: #ff2a2a;
            --text-main: #FFFFFF;
            --text-muted: #a1a1aa;
            --input-bg: rgba(255,255,255,0.06);
            --card-bg: rgba(255,255,255,0.06);
            --card-hover: rgba(255,255,255,0.10);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background:
                radial-gradient(circle at 10% 10%, rgba(229,9,20,0.15), transparent 40%),
                radial-gradient(circle at 90% 90%, rgba(99,102,241,0.12), transparent 40%),
                var(--bg-main);
            color: var(--text-main);
            min-height: 100vh;
            padding: 24px 16px 90px;
            -webkit-font-smoothing: antialiased;
        }

        .header {
            margin-bottom: 24px;
            text-align: left;
            animation: fadeInDown 0.5s ease;
        }

        .greeting {
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        .greeting-name {
            color: var(--accent);
            text-shadow: 0 0 18px rgba(229,9,20,0.4);
        }

        .subtitle {
            font-size: 14px;
            color: var(--text-muted);
        }

        .search-container {
            display: flex;
            gap: 10px;
            position: sticky;
            top: 10px;
            z-index: 10;
            margin-bottom: 20px;
            padding: 10px;
            background: rgba(0,0,0,0.35);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 12px;
        }

        .input-wrapper {
            position: relative;
            flex-grow: 1;
        }

        input[type="text"] {
            width: 100%;
            padding: 14px 44px 14px 16px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.08);
            background: var(--input-bg);
            color: var(--text-main);
            font-size: 15px;
            outline: none;
            transition: 0.2s;
        }

        input[type="text"]:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(229,9,20,0.15);
            background: rgba(255,255,255,0.08);
        }

        input::placeholder {
            color: #777;
        }

        .clear-icon {
            position: absolute;
            right: 14px;
            width: 20px;
            height: 20px;
            color: #8C8C8C;
            cursor: pointer;
            display: none;
        }

        .search-btn {
            background: linear-gradient(135deg, var(--accent), #ff3b3b);
            color: #fff;
            border: none;
            border-radius: 10px;
            padding: 0 22px;
            font-weight: 700;
            cursor: pointer;
            transition: 0.2s;
        }

        .search-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 20px rgba(229,9,20,0.25);
        }

        .section-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 12px;
        }

        .results-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .file-card {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--card-bg);
            border-radius: 12px;
            padding: 14px 16px;
            cursor: pointer;
            transition: 0.2s;
            border: 1px solid rgba(255,255,255,0.06);
            backdrop-filter: blur(10px);
        }

        .file-card:hover {
            background: var(--card-hover);
            transform: translateY(-2px);
            border-color: rgba(229,9,20,0.25);
        }

        .file-name {
            font-weight: 600;
            font-size: 15px;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .file-size {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 4px;
        }

        .get-icon {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(255,255,255,0.2);
            transition: 0.2s;
        }

        .file-card:hover .get-icon {
            background: var(--accent);
            border-color: var(--accent);
        }

        .pagination {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: calc(100% - 32px);
            max-width: 400px;
            display: none;
            justify-content: space-between;
            align-items: center;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(12px);
            padding: 12px 16px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.06);
        }

        .page-btn {
            background: rgba(255,255,255,0.08);
            color: var(--text-main);
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            cursor: pointer;
        }

        .page-indicator {
            font-size: 14px;
            color: var(--text-main);
        }

        .loader {
            text-align: center;
            padding: 40px 20px;
            color: var(--accent);
            display: none;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>

<body>

    <div class="header">
        <h1 class="greeting">Welcome, <span id="userName" class="greeting-name">Loading...</span></h1>
        <p class="subtitle">Find your favorite movies and series.</p>
    </div>

    <div class="search-container">
        <div class="input-wrapper">
            <input type="text" id="searchInput" placeholder="Titles, people, genres"
                   onkeypress="handleEnter(event)" oninput="toggleClearIcon()">
            <svg id="clearIcon" class="clear-icon" onclick="clearSearch()" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </div>
        <button class="search-btn" onclick="performSearch(0)">Search</button>
    </div>

    <h2 id="sectionTitle" class="section-title">Recently Added</h2>

    <div id="loader" class="loader">Loading files...</div>
    <div id="results" class="results-container"></div>

    <div id="pagination" class="pagination">
        <button id="backBtn" class="page-btn" onclick="changePage('back')">Back</button>
        <div id="pageIndicator" class="page-indicator">1/1</div>
        <button id="nextBtn" class="page-btn" onclick="changePage('next')">Next</button>
    </div>

<script>
    const tg = window.Telegram.WebApp;
    tg.expand();
    tg.setBackgroundColor('#0b0b0f');
    tg.setHeaderColor('#0b0b0f');

    const user = tg.initDataUnsafe?.user;
    document.getElementById('userName').innerText = user?.first_name || "Guest";

    let currentQuery = '';
    let currentOffset = 0;
    let nextOffset = null;
    let botUsername = '';
    let maxResultsPerPage = 10;

    function handleEnter(e){ if(e.key==='Enter') performSearch(0); }

    function toggleClearIcon(){
        const input=document.getElementById('searchInput');
        document.getElementById('clearIcon').style.display = input.value ? 'block':'none';
        if(!input.value) performSearch(0);
    }

    function clearSearch(){
        document.getElementById('searchInput').value='';
        toggleClearIcon();
        performSearch(0);
    }

    async function performSearch(offset=0){
        const query=document.getElementById('searchInput').value.trim();
        currentQuery=query;
        currentOffset=offset;

        document.getElementById('loader').style.display='block';
        document.getElementById('results').innerHTML='';

        const res=await fetch(`/api/search?q=${encodeURIComponent(query)}&offset=${offset}`);
        const data=await res.json();

        botUsername=data.bot_username;
        maxResultsPerPage=data.max_btn;

        document.getElementById('loader').style.display='none';
        renderResults(data);
        renderPagination(data);
    }

    function renderResults(data){
        const box=document.getElementById('results');
        if(!data.files?.length){
            box.innerHTML="No results";
            return;
        }

        data.files.forEach(f=>{
            const div=document.createElement('div');
            div.className='file-card';
            div.innerHTML=`
                <div>
                    <div class="file-name">${f.name}</div>
                    <div class="file-size">${f.size} HD</div>
                </div>
                <div class="get-icon">▶</div>
            `;
            div.onclick=()=>{
                const link=`https://t.me/${botUsername}?start=file_${f.id}`;
                tg.openTelegramLink(link);
            };
            box.appendChild(div);
        });
    }

    function renderPagination(data){
        nextOffset=data.next_offset;
        document.getElementById('pagination').style.display='flex';
        document.getElementById('pageIndicator').innerText="Updated";
    }

    function changePage(dir){
        if(dir==='next'&&nextOffset!==null) performSearch(nextOffset);
        if(dir==='back'){
            let prev=currentOffset-maxResultsPerPage;
            if(prev<0) prev=0;
            performSearch(prev);
        }
    }

    window.onload=()=>performSearch(0);
</script>

</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Backend helpers
# ─────────────────────────────────────────────────────────────────────────────
async def media_watch(message_id):
    media_msg = await temp.BOT.get_messages(BIN_CHANNEL, message_id)
    media = getattr(media_msg, media_msg.media.value, None)
    src = urllib.parse.urljoin(URL, f'download/{message_id}')
    tag = media.mime_type.split('/')[0].strip()
    if tag == 'video':
        heading = html.escape(f'Watch — {media.file_name}')
        html_ = (watch_tmplt
                 .replace('{heading}',   heading)
                 .replace('{file_name}', media.file_name)
                 .replace('{src}',       src))
    else:
        html_ = error_tmplt
    return html_
