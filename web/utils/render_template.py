from info import BIN_CHANNEL, URL
from utils import temp
from web.utils.custom_dl import TGCustomYield
import urllib.parse
import html

# ─────────────────────────────────────────────────────────────────────────────
# 1. INFINITY WATCH WEBAPP TEMPLATE (TMDB POSTER LAYOUT + CYBERPUNK THEME)
# ─────────────────────────────────────────────────────────────────────────────
webapp_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Infinity Watch</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #08090d;
            --surface: #11131a;
            --accent: #8b5cf6;
            --accent-cyan: #00ffff;
            --accent-glow: rgba(139, 92, 246, 0.4);
            --cyan-glow: rgba(0, 255, 255, 0.3);
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; -webkit-tap-highlight-color: transparent;}
        body { background: var(--bg-dark); color: var(--text-main); overflow-x: hidden; }
        
        /* Navbar */
        .navbar {
            position: fixed; top: 0; width: 100%; padding: 15px 20px; z-index: 1000;
            background: linear-gradient(to bottom, rgba(8,9,13,0.95) 0%, transparent 100%);
            display: flex; justify-content: space-between; align-items: center; transition: 0.3s;
        }
        .navbar.scrolled { background: rgba(8,9,13,0.95); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(139, 92, 246, 0.2); }
        .logo { 
            font-size: 22px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px var(--cyan-glow);
        }
        .nav-icons { display: flex; gap: 15px; align-items: center; }
        .icon-btn { font-size: 20px; cursor: pointer; color: var(--accent-cyan); font-weight: 800; background: none; border: none; }
        .info-btn { border: 1px solid var(--accent); border-radius: 50%; width: 30px; height: 30px; font-size: 15px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px var(--accent-glow); color: var(--accent-cyan);}

        /* Search Bar */
        .search-bar {
            position: fixed; top: 0; left: 0; width: 100%; padding: 20px; background: var(--surface);
            z-index: 1001; transform: translateY(-100%); transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex; gap: 10px; align-items: center; border-bottom: 1px solid var(--accent);
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        .search-bar.active { transform: translateY(0); }
        .input-wrapper { position: relative; flex: 1; }
        .search-bar input {
            width: 100%; padding: 12px 60px 12px 20px; border-radius: 30px; border: 1px solid rgba(139, 92, 246, 0.3); outline: none;
            background: #1a1d27; color: #fff; font-size: 16px; transition: 0.3s;
        }
        .search-bar input:focus { border-color: var(--accent-cyan); box-shadow: 0 0 15px var(--cyan-glow); }
        .clear-text { position: absolute; right: 15px; top: 50%; transform: translateY(-50%); font-size: 12px; color: var(--accent-cyan); font-weight: 700; cursor: pointer; display: none; text-transform: uppercase;}
        .close-search { color: var(--text-dim); font-weight: 600; cursor: pointer; padding: 10px; }

        /* Hero Section */
        .hero {
            position: relative; height: 75vh; display: flex; align-items: flex-end; padding: 40px 20px;
            background-size: cover; background-position: center top; transition: background-image 0.5s ease-in-out;
        }
        .hero::after {
            content: ''; position: absolute; inset: 0;
            background: linear-gradient(to top, var(--bg-dark) 0%, rgba(8,9,13,0.4) 50%, rgba(8,9,13,0.1) 100%);
        }
        .hero-content { position: relative; z-index: 10; width: 100%; max-width: 600px; }
        .hero-title { font-size: 38px; font-weight: 800; line-height: 1.1; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); color: #fff;}
        .hero-meta { font-size: 14px; color: var(--accent-cyan); margin-bottom: 15px; font-weight: 700; }
        .hero-meta span { border: 1px solid rgba(0,255,255,0.3); background: rgba(0,255,255,0.1); padding: 2px 8px; border-radius: 6px; margin-right: 8px; font-size: 11px;}
        .hero-desc { font-size: 14px; line-height: 1.5; color: #cbd5e1; margin-bottom: 20px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
        .btn-play {
            background: linear-gradient(135deg, var(--accent), var(--accent-cyan)); color: #000; border: none; padding: 12px 30px; border-radius: 12px;
            font-size: 16px; font-weight: 800; cursor: pointer; display: flex; align-items: center; gap: 8px;
            transition: 0.2s; text-transform: uppercase; box-shadow: 0 5px 15px var(--accent-glow);
        }
        .btn-play:active { transform: scale(0.95); }

        /* Rows */
        .row-container { padding: 20px 0 20px 20px; }
        .row-title { font-size: 18px; font-weight: 700; margin-bottom: 15px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px;}
        .row { display: flex; overflow-x: auto; gap: 12px; padding-bottom: 15px; scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch;}
        .row::-webkit-scrollbar { display: none; }
        .card { flex: 0 0 130px; scroll-snap-align: start; position: relative; border-radius: 12px; overflow: hidden; cursor: pointer; transition: 0.3s; border: 1px solid rgba(139, 92, 246, 0.1);}
        .card:active { transform: scale(0.95); border-color: var(--accent-cyan); box-shadow: 0 0 15px var(--cyan-glow);}
        .card img { width: 100%; height: 195px; object-fit: cover; background: #222; }
        
        /* Modals */
        .modal-overlay {
            position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 2000;
            display: none; justify-content: center; align-items: flex-end; backdrop-filter: blur(5px);
        }
        .modal {
            background: var(--surface); width: 100%; max-height: 85vh; border-radius: 24px 24px 0 0;
            padding: 24px; transform: translateY(100%); transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            overflow-y: auto; border-top: 1px solid var(--accent); box-shadow: 0 -10px 30px var(--accent-glow);
        }
        .modal.open { transform: translateY(0); }
        .modal-drag { width: 40px; height: 5px; background: rgba(139, 92, 246, 0.5); border-radius: 10px; margin: 0 auto 20px; }
        .m-title { font-size: 22px; font-weight: 800; margin-bottom: 5px; color: #fff;}
        .m-meta { font-size: 13px; color: var(--accent-cyan); margin-bottom: 15px; font-weight: 600;}
        .m-files { display: flex; flex-direction: column; gap: 10px; margin-top: 20px;}
        .m-file-card {
            background: #1a1d27; border: 1px solid rgba(139, 92, 246, 0.2); padding: 15px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; transition: 0.2s;
        }
        .m-file-card:active { border-color: var(--accent-cyan); }
        .m-file-name { font-size: 14px; font-weight: 600; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; color: #fff;}
        .m-file-size { font-size: 11px; color: var(--accent-cyan); margin-top: 6px; font-weight: 800; background: rgba(0,255,255,0.1); padding: 2px 6px; border-radius: 4px; display: inline-block;}
        .m-btn { background: var(--accent); color: #fff; border:none; padding: 8px 16px; border-radius: 8px; font-weight: 700; font-size: 13px;}
        
        /* Info Popup */
        .info-modal { display: none; justify-content: center; align-items: center; position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 3000; backdrop-filter: blur(5px);}
        .info-content { background: var(--surface); border: 1px solid var(--accent-cyan); padding: 25px; border-radius: 20px; text-align: center; max-width: 300px; animation: pop 0.3s;}
        @keyframes pop { from { transform: scale(0.8); opacity:0;} to { transform: scale(1); opacity:1;}}
        .info-content h3 { color: var(--accent-cyan); margin-bottom: 15px; font-weight: 800;}
        .info-content p { color: var(--text-dim); font-size: 14px; line-height: 1.6; margin-bottom: 20px;}

        .loader-full { position: fixed; inset:0; background: var(--bg-dark); z-index: 5000; display: flex; justify-content: center; align-items: center; color: var(--accent-cyan); font-weight: 800; font-size: 24px; letter-spacing: 2px; text-transform: uppercase; animation: pulse 1s infinite;}
        @keyframes pulse { 50% { opacity: 0.5; transform: scale(0.95);} }
    </style>
</head>
<body>

    <div id="mainLoader" class="loader-full">INFINITY SYSTEM</div>

    <nav class="navbar" id="navbar">
        <div class="logo">Infinity</div>
        <div class="nav-icons">
            <button class="icon-btn info-btn" onclick="document.getElementById('infoPopup').style.display='flex'">i</button>
            <div class="icon-btn" onclick="toggleSearch(true)">🔍</div>
        </div>
    </nav>

    <div id="infoPopup" class="info-modal" onclick="this.style.display='none'">
        <div class="info-content" onclick="event.stopPropagation()">
            <h3>📝 Instructions</h3>
            <p>1. Browse trending collections directly.<br>2. Use Search to find specific content.<br>3. Tap a poster to check database availability.</p>
            <button class="btn-play" style="width:100%; justify-content:center; padding: 10px;" onclick="document.getElementById('infoPopup').style.display='none'">Understood</button>
        </div>
    </div>

    <div class="search-bar" id="searchBar">
        <div class="input-wrapper">
            <input type="text" id="searchInput" placeholder="Search Movies, Series..." onkeyup="handleSearch(event)">
            <div id="clearText" class="clear-text" onclick="clearSearch()">Clear</div>
        </div>
        <div class="close-search" onclick="toggleSearch(false)">Cancel</div>
    </div>

    <div class="hero" id="hero" style="background-image: url('');">
        <div class="hero-content">
            <h1 class="hero-title" id="hTitle">Loading...</h1>
            <div class="hero-meta"><span id="hYear">----</span> <span id="hRating">⭐ --</span></div>
            <p class="hero-desc" id="hDesc">Syncing with Elite Network...</p>
            <button class="btn-play" id="hPlay" onclick="">▶ Check Files</button>
        </div>
    </div>

    <div id="contentRows"></div>

    <div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
        <div class="modal" id="modalContent" onclick="event.stopPropagation()">
            <div class="modal-drag"></div>
            <h2 class="m-title" id="mTitle">Movie Title</h2>
            <div class="m-meta" id="mMeta">Scanning Database...</div>
            <div class="m-files" id="mFilesList">
                </div>
        </div>
    </div>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();
        tg.setBackgroundColor('#08090d');
        tg.setHeaderColor('#08090d');

        let botUsername = '';

        window.addEventListener('scroll', () => {
            document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 50);
        });

        function toggleSearch(show) {
            const bar = document.getElementById('searchBar');
            bar.classList.toggle('active', show);
            if(show) {
                document.getElementById('searchInput').focus();
            } else {
                clearSearch();
            }
        }

        function clearSearch() {
            document.getElementById('searchInput').value = '';
            document.getElementById('clearText').style.display = 'none';
            loadHomeData(); // Reset to home
        }

        async function loadHomeData() {
            document.getElementById('mainLoader').style.display = 'flex';
            document.getElementById('contentRows').innerHTML = '';
            try {
                const res = await fetch('/api/tmdb-trending');
                const data = await res.json();
                botUsername = data.bot_username;

                // Setup Hero
                if(data.hero) {
                    document.getElementById('hero').style.backgroundImage = `url('${data.hero.backdrop}')`;
                    document.getElementById('hTitle').innerText = data.hero.title;
                    document.getElementById('hYear').innerText = data.hero.type === 'movie' ? 'MOVIE' : 'SERIES';
                    document.getElementById('hRating').innerText = `⭐ ${data.hero.rating}`;
                    document.getElementById('hDesc').innerText = data.hero.overview;
                    document.getElementById('hPlay').onclick = () => openModal(data.hero.title);
                }

                // Render Rows (TMDB generates these dynamically)
                renderRow('🔥 Trending Now', data.trending);
                renderRow('🍿 Popular Movies', data.popular_movies);
                renderRow('📺 Top Rated TV Shows', data.popular_tv);
                
                document.getElementById('mainLoader').style.display = 'none';
            } catch (e) {
                document.getElementById('mainLoader').innerText = 'NETWORK ERROR';
            }
        }

        function renderRow(title, items) {
            if(!items || items.length === 0) return;
            let cards = items.map(i => `
                <div class="card" onclick="openModal('${i.title.replace(/'/g, "\\'")}')">
                    <img src="${i.poster || 'https://via.placeholder.com/130x195?text=No+Poster'}" alt="${i.title}" loading="lazy">
                </div>
            `).join('');

            const rowHtml = `
                <div class="row-container">
                    <div class="row-title">${title}</div>
                    <div class="row">${cards}</div>
                </div>
            `;
            document.getElementById('contentRows').insertAdjacentHTML('beforeend', rowHtml);
        }

        let searchTimeout;
        function handleSearch(e) {
            const query = e.target.value.trim();
            document.getElementById('clearText').style.display = query.length > 0 ? 'block' : 'none';
            
            clearTimeout(searchTimeout);
            if(query.length < 3) {
                if(query.length === 0) loadHomeData();
                return;
            }
            searchTimeout = setTimeout(async () => {
                document.getElementById('contentRows').innerHTML = '<div style="text-align:center; margin-top: 50px; color: var(--accent-cyan); font-weight:bold;">SCANNING NETWORK...</div>';
                const res = await fetch(`/api/tmdb-search?q=${encodeURIComponent(query)}`);
                const data = await res.json();
                document.getElementById('contentRows').innerHTML = '';
                renderRow('Search Results', data.results);
            }, 600);
        }

        async function openModal(title) {
            const overlay = document.getElementById('modalOverlay');
            const modal = document.getElementById('modalContent');
            const filesList = document.getElementById('mFilesList');
            
            document.getElementById('mTitle').innerText = title;
            document.getElementById('mMeta').innerText = "Scanning Bot Database...";
            filesList.innerHTML = '';
            
            overlay.style.display = 'flex';
            setTimeout(() => modal.classList.add('open'), 10);

            try {
                // Search in Bot Database directly
                const res = await fetch(`/api/search?q=${encodeURIComponent(title)}`);
                const data = await res.json();
                
                if(!data.files || data.files.length === 0) {
                    document.getElementById('mMeta').innerText = "⚠️ Content not available in database yet.";
                    filesList.innerHTML = `
                        <button class="btn-play" style="width:100%; justify-content:center; font-size:14px;" onclick="requestMovie('${title}')">
                            Request to Admin
                        </button>`;
                    return;
                }

                document.getElementById('mMeta').innerText = `✅ Found ${data.total_results} files ready for extraction!`;
                
                let fileHtml = '';
                data.files.slice(0, 10).forEach(file => {
                    fileHtml += `
                        <div class="m-file-card">
                            <div style="flex:1; padding-right:10px;">
                                <div class="m-file-name">${file.name}</div>
                                <div class="m-file-size">${file.size}</div>
                            </div>
                            <button class="m-btn" onclick="getFile('${file.id}')">GET</button>
                        </div>
                    `;
                });
                
                if(data.total_results > 10) {
                    fileHtml += `<button class="btn-play" style="width:100%; justify-content:center; background:#1a1d27; color:#00ffff; border: 1px solid #00ffff; margin-top:10px;" onclick="getFile('all_search_${title}')">View All Results in Bot</button>`;
                }
                
                filesList.innerHTML = fileHtml;

            } catch (e) {
                document.getElementById('mMeta').innerText = "Error connecting to bot system.";
            }
        }

        function closeModal(e) {
            if(e.target === document.getElementById('modalOverlay') || e === 'force') {
                document.getElementById('modalContent').classList.remove('open');
                setTimeout(() => document.getElementById('modalOverlay').style.display = 'none', 300);
            }
        }

        function getFile(fileId) {
            const payload = fileId.startsWith('all_') ? '' : `file_${fileId}`; 
            const link = `https://t.me/${botUsername}?start=${payload}`;
            tg.openTelegramLink(link);
            setTimeout(() => tg.close(), 100);
        }

        function requestMovie(title) {
            tg.sendData(JSON.stringify({action: "request", title: title}));
            tg.close();
        }

        window.onload = loadHomeData;
    </script>
</body>
</html>
"""

# ─────────────────────────────────────────────────────────────────────────────
# 2. PAYMENT & PREMIUM PLAN WEBAPP TEMPLATE (MATCHING CYBERPUNK THEME)
# ─────────────────────────────────────────────────────────────────────────────
payment_tmplt = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Upgrade to Premium</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #08090d; --surface: #11131a; 
            --primary: #00ffff; --secondary: #8b5cf6; --magenta: #ff00ff;
            --primary-glow: rgba(0, 255, 255, 0.4); 
            --text: #f8fafc; --text-muted: #94a3b8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; -webkit-tap-highlight-color: transparent;}
        body { background: var(--bg); color: var(--text); padding: 20px; overflow-x: hidden; }
        
        .header { text-align: center; margin-bottom: 30px; margin-top: 10px; }
        .title { 
            font-size: 26px; font-weight: 800; 
            background: linear-gradient(90deg, #fff, var(--primary)); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
        }
        .subtitle { font-size: 14px; color: var(--text-muted); margin-top: 5px; text-transform: uppercase; letter-spacing: 1px;}

        .plans-grid { display: grid; gap: 15px; margin-bottom: 30px; }
        .plan-card {
            background: var(--surface); border: 1px solid var(--secondary); border-radius: 16px; padding: 20px;
            display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: 0.3s;
        }
        .plan-card.active { border-color: var(--primary); box-shadow: 0 0 20px var(--primary-glow); transform: scale(1.02); }
        .plan-days { font-size: 18px; font-weight: 800; color: #fff; }
        .plan-price { font-size: 22px; font-weight: 800; color: var(--primary); }
        .plan-currency { font-size: 12px; color: var(--text-muted); }

        .payment-box {
            background: var(--surface); border-radius: 20px; padding: 25px 20px; text-align: center;
            border: 1px solid var(--secondary); display: none; animation: slideUp 0.4s ease;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        @keyframes slideUp { from { transform: translateY(20px); opacity: 0;} to { transform: translateY(0); opacity: 1;} }
        
        .qr-img { width: 180px; height: 180px; border-radius: 12px; border: 2px solid var(--primary); padding: 5px; background: #fff; margin-bottom: 15px; box-shadow: 0 0 15px var(--primary-glow);}
        .upi-box {
            background: #050508; padding: 12px; border-radius: 10px; border: 1px dashed var(--magenta);
            font-size: 15px; font-family: monospace; color: #fff; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;
        }
        .copy-btn { background: var(--secondary); color: #fff; border: none; padding: 5px 12px; border-radius: 6px; font-weight: 700; cursor: pointer; text-transform: uppercase;}
        
        .action-btn {
            background: linear-gradient(135deg, var(--secondary), var(--primary)); color: #000; border: none; width: 100%;
            padding: 16px; border-radius: 12px; font-size: 16px; font-weight: 800; cursor: pointer; text-transform: uppercase; letter-spacing: 1px;
            box-shadow: 0 10px 20px rgba(139, 92, 246, 0.4);
        }
        .action-btn:active { transform: scale(0.98); }
    </style>
</head>
<body>

    <div class="header">
        <h1 class="title">Unlock Premium</h1>
        <p class="subtitle">Join the Elite Network</p>
    </div>

    <div class="plans-grid" id="plansContainer">
        </div>

    <div class="payment-box" id="paymentBox">
        <h3 style="margin-bottom: 15px; font-weight: 800; color: #fff;">Scan to Pay <span id="payAmount" style="color: var(--primary);"></span></h3>
        <img src="{qr_code}" alt="QR Code" class="qr-img">
        
        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 5px;">Or pay using UPI ID:</p>
        <div class="upi-box">
            <span id="upiId">{upi_id}</span>
            <button class="copy-btn" onclick="copyUpi()">Copy</button>
        </div>

        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 15px; line-height: 1.5;">
            After successful payment, take a screenshot and send it to the Bot Admin to activate your plan.
        </p>

        <button class="action-btn" onclick="sendScreenshot()">Send Screenshot</button>
    </div>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();
        tg.setBackgroundColor('#08090d');
        tg.setHeaderColor('#08090d');

        const botUsername = "{bot_username}";
        const plans = {plans}; 
        
        let selectedPlan = null;
        let selectedPrice = null;
        let selectedCurrency = null;

        function renderPlans() {
            const container = document.getElementById('plansContainer');
            Object.keys(plans).forEach(days => {
                const currency = plans[days][0];
                const price = plans[days][1];
                let planName = days == 30 ? "1 Month" : days == 90 ? "3 Months" : days == 180 ? "6 Months" : days == 7 ? "1 Week" : `${days} Days`;

                const card = document.createElement('div');
                card.className = 'plan-card';
                card.innerHTML = `
                    <div class="plan-days">${planName}</div>
                    <div style="text-align:right;">
                        <span class="plan-currency">${currency}</span>
                        <span class="plan-price">${price}</span>
                    </div>
                `;
                card.onclick = () => selectPlan(card, days, price, currency);
                container.appendChild(card);
            });
        }

        function selectPlan(element, days, price, currency) {
            document.querySelectorAll('.plan-card').forEach(el => el.classList.remove('active'));
            element.classList.add('active');
            
            selectedPlan = days;
            selectedPrice = price;
            selectedCurrency = currency;

            document.getElementById('payAmount').innerText = `${currency} ${price}`;
            document.getElementById('paymentBox').style.display = 'block';
            
            setTimeout(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }), 100);
        }

        function copyUpi() {
            const upi = document.getElementById('upiId').innerText;
            navigator.clipboard.writeText(upi);
            tg.showAlert("UPI ID Copied!");
        }

        function sendScreenshot() {
            if(!selectedPlan) return;
            tg.sendData(JSON.stringify({
                action: "payment_screenshot",
                plan: selectedPlan,
                amount: selectedPrice
            }));
            tg.close();
        }

        window.onload = renderPlans;
    </script>
</body>
</html>
"""

# ─────────────────────────────────────────────────────────────────────────────
# 3. WATCH PAGE TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────
watch_tmplt = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{heading}</title>
    <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
    <style>
        :root {
            --p:#818cf8; --p2:#6366f1; --sec:#a78bfa; --acc:#38bdf8;
            --txt:#f1f5f9; --txt2:#94a3b8;
            --bg:#020617; --glass:rgba(10,18,38,.8); --gb:rgba(129,140,248,.13);
        }
        *, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }
        body {
            font-family:'Inter',sans-serif;
            background:var(--bg); color:var(--txt);
            min-height:100vh;
            display:flex; flex-direction:column;
            overflow-x:hidden;
        }
        body::before {
            content:''; position:fixed; inset:0; z-index:-1;
            background:
                radial-gradient(ellipse 75% 50% at 10% 20%, rgba(99,102,241,.12) 0%, transparent 58%),
                radial-gradient(ellipse 60% 40% at 90% 80%, rgba(167,139,250,.09) 0%, transparent 55%),
                linear-gradient(160deg, #020617 0%, #070c1b 45%, #0f172a 100%);
        }

        /* Header */
        header {
            padding:.8rem 1.5rem;
            backdrop-filter:blur(24px) saturate(180%);
            -webkit-backdrop-filter:blur(24px) saturate(180%);
            background:var(--glass);
            border-bottom:1px solid var(--gb);
            display:flex; flex-direction:column; align-items:center; justify-content:center;
            box-shadow:0 1px 32px rgba(0,0,0,.45);
        }
        .header-logo {
            font-size:1rem; font-weight:800; letter-spacing:-.01em;
            background:linear-gradient(90deg,#e2e8f0 0%,var(--p) 50%,var(--acc) 100%);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
        }
        #file-name {
            font-size:.82rem; color:var(--txt2); margin-top:.3rem; font-weight:500;
            white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
            max-width:100%; text-align:center;
        }

        /* Container */
        .container {
            flex:1; display:flex; flex-direction:column; align-items:center;
            padding:2.5rem 1.5rem 3rem; width:100%;
        }

        /* Badge */
        .badge {
            display:inline-flex; align-items:center; gap:.4rem;
            background:rgba(16,185,129,.12); border:1px solid rgba(16,185,129,.3);
            padding:.3rem .9rem; border-radius:30px;
            font-size:.7rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase; color:#10b981;
            margin-bottom:1.5rem; backdrop-filter:blur(8px);
        }
        .badge-dot {
            width:6px; height:6px; background:#10b981; border-radius:50%;
            box-shadow:0 0 10px #10b981; animation:pulse 2s cubic-bezier(.4,0,.6,1) infinite;
        }
        @keyframes pulse { 50% { opacity:.3; box-shadow:none; } }

        /* Player Wrap */
        .player-wrap {
            position:relative; width:100%; max-width:1060px;
            border-radius:24px; padding:1px; z-index:10;
        }
        .player-ambient {
            position:absolute; inset:-2px; z-index:-1;
            background:linear-gradient(135deg,rgba(99,102,241,.4),rgba(167,139,250,.2),rgba(56,189,248,.3));
            filter:blur(35px); opacity:.3; transform:translateZ(0); border-radius:inherit;
        }
        .player-card {
            position:relative; background:#000; border-radius:22px;
            overflow:hidden; box-shadow:0 25px 65px rgba(0,0,0,.5);
            aspect-ratio:16/9; display:flex; align-items:center; justify-content:center;
            width:100%;
        }
        .player-card video, .plyr video {
            width:100% !important; height:100% !important;
            object-fit:cover !important; border-radius:22px;
        }

        /* Load Skeleton */
        .skeleton {
            position:absolute; inset:0; background:#0a0e1c; z-index:20;
            overflow:hidden; pointer-events:none; transition:opacity .4s, visibility .4s;
        }
        .skeleton::after {
            content:''; position:absolute; inset:0;
            background:linear-gradient(90deg,transparent,rgba(129,140,248,.08),transparent);
            transform:translateX(-100%); animation:shimmer 1.8s infinite;
        }
        @keyframes shimmer { 100% { transform:translateX(100%); } }
        .skeleton.gone { opacity:0; visibility:hidden; }

        /* Video Error Overlay */
        .player-err-overlay {
            position:absolute; inset:0; z-index:50;
            background:rgba(2,6,23,.92); backdrop-filter:blur(14px);
            opacity:0; visibility:hidden;
            display:flex; align-items:center; justify-content:center;
            border-radius:22px; text-align:center; padding:2rem;
            transition:opacity .4s ease, visibility .4s ease;
        }
        .player-err-overlay.show { opacity:1; visibility:visible; }
        .err-card-sm { max-width:440px; width:100%; }
        .err-card-sm h2 { font-size:1.4rem; font-weight:800; margin-bottom:.5rem; letter-spacing:-.02em; }
        .err-card-sm p { font-size:.85rem; color:var(--txt2); margin-bottom:1.5rem; line-height:1.5; }
        .err-btn-grid {
            display:grid; grid-template-columns:repeat(3, 1fr); gap:.6rem; margin-top:1.2rem;
        }

        /* Buttons */
        .btn-row {
            display:grid; grid-template-columns:repeat(3, 1fr); gap:.8rem;
            margin-top:1.2rem;
            width:100%; max-width:1060px;
        }
        .xbtn {
            position:relative; overflow:hidden;
            display:flex; align-items:center; justify-content:center; gap:.5rem;
            width:100%; padding:.72rem .9rem;
            border-radius:11px; border:none;
            font-family:'Inter',sans-serif;
            font-size:.84rem; font-weight:600;
            letter-spacing:.01em;
            cursor:pointer; text-decoration:none; color:#fff;
            transition:transform .2s, box-shadow .2s, filter .2s;
        }
        .xbtn::after {
            content:''; position:absolute; inset:0;
            background:rgba(255,255,255,.08);
            opacity:0; transition:opacity .18s;
        }
        .xbtn:hover::after { opacity:1; }
        .xbtn:hover {
            transform:scale(1.02);
            filter:brightness(1.08);
        }
        .xbtn:active { transform:scale(.98); }

        /* Download – indigo */
        .btn-dl {
            background:linear-gradient(135deg,#4f46e5,#818cf8,#a78bfa);
            box-shadow:0 4px 16px rgba(99,102,241,.38);
        }
        .btn-dl:hover { box-shadow:0 7px 24px rgba(99,102,241,.55); }

        /* VLC – amber */
        .btn-vlc {
            background:linear-gradient(135deg,#92400e,#f59e0b,#fde68a);
            box-shadow:0 4px 16px rgba(245,158,11,.35);
        }
        .btn-vlc:hover { box-shadow:0 7px 24px rgba(245,158,11,.52); }

        /* MX – emerald */
        .btn-mx {
            background:linear-gradient(135deg,#065f46,#10b981,#6ee7b7);
            box-shadow:0 4px 16px rgba(16,185,129,.35);
        }
        .btn-mx:hover { box-shadow:0 7px 24px rgba(16,185,129,.52); }

        /* Footer */
        footer {
            padding:.85rem 1.5rem; text-align:center;
            color:var(--txt2); font-size:.73rem;
            margin-top:auto;
        }
        footer::before {
            content:''; display:block;
            width:90px; height:1px;
            background:linear-gradient(90deg,transparent,rgba(129,140,248,.28),transparent);
            margin:0 auto .7rem;
        }
        .ha-link {
            color:var(--p); text-decoration:none; font-weight:600;
            transition:opacity .2s;
        }
        .ha-link:hover { opacity:.7; }

        /* Plyr overrides */
        .plyr { width: 100% !important; height: 100% !important; }
        .plyr__controls {
            width: 100% !important;
            bottom: 0 !important;
            padding: 10px 15px !important;
            justify-content: space-between !important;
        }
        .plyr__progress { flex-grow: 1 !important; display: flex !important; }
        .plyr--video .plyr__control--overlaid {
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            background:linear-gradient(135deg,var(--p2),var(--sec));
            box-shadow:0 0 20px rgba(129,140,248,.5);
            transition:opacity .2s ease, box-shadow .2s ease !important;
        }
        .plyr--video .plyr__control--overlaid:hover {
            transform: translate(-50%, -50%) !important;
            box-shadow:0 0 30px rgba(129,140,248,.7);
        }
        .plyr--video .plyr__control:hover,
        .plyr--video .plyr__control[aria-expanded="true"] { background:var(--p2); }
        .plyr__control.plyr__tab-focus { box-shadow:0 0 0 5px rgba(99,102,241,.4); }
        .plyr--full-ui input[type=range]  { color:var(--p); }
        .plyr__progress input[type=range] { color:var(--p); }
        .plyr__progress__buffer { color:rgba(129,140,248,.2); }
        .plyr__menu__container .plyr__control[role=menuitemradio][aria-checked=true]::before { background:var(--p); }

        /* Responsive */
        @media (max-width:600px) {
            .container { padding:1rem .85rem .85rem; }
            .btn-row, .err-btn-grid { grid-template-columns:1fr; gap:.6rem; }
            .xbtn { padding:.78rem 1rem; }
            #file-name { font-size:.78rem; }
        }
    </style>
</head>
<body>

<header>
    <span class="header-logo">Infinity Botz</span>
    <div id="file-name">{file_name}</div>
</header>

<div class="container">

    <div class="badge">
        <span class="badge-dot"></span>
        ONLINE
    </div>

    <div class="player-wrap">
        <div class="player-ambient"></div>
        <div class="player-card">
            <div class="skeleton" id="skel"></div>

            <div class="player-err-overlay" id="vidErr">
                <div class="err-card-sm">
                    <div style="margin-bottom:1.2rem; color:rgba(255,255,255,0.7);">
                        <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                    </div>
                    <h2>Oops! The video failed to load.</h2>
                    <p>Please try downloading or opening it in an external player.</p>
                </div>
            </div>

            <video src="{src}" class="player" playsinline controls></video>
        </div>
    </div>

    <div class="btn-row">
        <a href="{src}" class="xbtn btn-dl" download>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            Download
        </a>

        <a href="vlc://{src}" class="xbtn btn-vlc">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            Play in VLC
        </a>

        <a href="intent:{src}#Intent;package=com.mxtech.videoplayer.ad;end" class="xbtn btn-mx">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <polygon points="10 8 16 12 10 16 10 8"/>
            </svg>
            MX Player
        </a>
    </div>

</div>

<footer>
    <p>Powered by <a href="https://t.me/infinity_botzz" class="ha-link" target="_blank" rel="noopener">Infinity Botz</a></p>
</footer>

<script src="https://cdn.plyr.io/3.7.8/plyr.js"></script>
<script>
document.addEventListener('DOMContentLoaded', () => {
    const skel    = document.getElementById('skel');
    const vidErr  = document.getElementById('vidErr');
    const videoEl = document.querySelector('.player');

    const player = new Plyr('.player', {
        controls: ['play-large','play','progress','current-time','duration',
                   'mute','volume','captions','settings','pip','airplay','fullscreen'],
        settings: ['captions','quality','speed'],
        hideControls: false,
        tooltips: { controls:true, seek:true }
    });

    let errTriggered = false;
    const hideSkel = () => { if (skel) skel.classList.add('gone'); };
    const showError = () => {
        if (errTriggered) return;
        errTriggered = true;
        hideSkel();
        if (vidErr) vidErr.classList.add('show');
        if (player && player.elements && player.elements.container) {
            player.elements.container.style.display = 'none';
        }
    };
    
    videoEl.addEventListener('loadedmetadata', hideSkel);
    videoEl.addEventListener('canplay', hideSkel);
    
    // Core HTML5 error events
    ['error', 'abort', 'stalled'].forEach(evt => {
        videoEl.addEventListener(evt, () => {
            if (videoEl.error || videoEl.networkState === 3) showError();
        });
    });
    
    // Fallback timeout for unresponsive streams
    let loadTimeout = setTimeout(() => {
        if (videoEl.readyState === 0) showError();
        hideSkel();
    }, 12000);
    
    videoEl.addEventListener('playing', () => clearTimeout(loadTimeout));
});
</script>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# 4. ERROR PAGE TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────
error_tmplt = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error — ɪɴꜰɪɴɪᴛʏ ʙᴏᴛᴢ</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap">
    <style>
        :root {
            --p:#8b5cf6; --p2:#7c3aed; --sec:#a78bfa; --acc:#c4b5fd;
            --txt:#f8fafc; --txt2:#94a3b8;
            --bg:#08090d; --glass:rgba(17, 19, 26, 0.85); --gb:rgba(139, 92, 246, 0.15);
            --err:#f43f5e; --err2:rgba(244, 63, 94, 0.1);
        }
        *, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }
        body {
            font-family:'Plus Jakarta Sans',sans-serif;
            background:var(--bg);
            color:var(--txt);
            min-height:100vh;
            display:flex;
            flex-direction:column;
            overflow-x:hidden;
        }
        body::before {
            content:''; position:fixed; inset:0; z-index:-1;
            background:
                radial-gradient(ellipse 65% 45% at 50% 40%, rgba(139, 92, 246, 0.08) 0%, transparent 65%),
                radial-gradient(ellipse 75% 50% at 10% 20%, rgba(124, 58, 237, 0.05) 0%, transparent 60%),
                linear-gradient(160deg, #08090d 0%, #0c0d14 45%, #11131a 100%);
        }

        /* Header */
        header {
            padding:1.2rem 1.5rem;
            backdrop-filter:blur(24px);
            -webkit-backdrop-filter:blur(24px);
            background:var(--glass);
            border-bottom:1px solid var(--gb);
            display:flex; justify-content:center; align-items:center;
            animation:fadeDown .45s ease both;
        }
        @keyframes fadeDown {
            from { opacity:0; transform:translateY(-12px); }
            to   { opacity:1; transform:translateY(0); }
        }
        .header-logo {
            font-size:1.1rem; font-weight:800; letter-spacing:0.05em;
            background:linear-gradient(90deg,#f8fafc 0%,var(--p) 50%,var(--acc) 100%);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
            text-transform: uppercase;
        }

        /* Error layout */
        main {
            flex:1; display:flex; align-items:center; justify-content:center;
            padding:3rem 1.25rem;
        }
        .error-card {
            background:var(--glass);
            border:1px solid rgba(139, 92, 246, 0.2);
            border-radius:24px;
            padding:3rem 2rem;
            text-align:center;
            max-width:420px; width:100%;
            box-shadow:
                0 0 0 1px rgba(255,255,255,.03),
                0 20px 50px rgba(0,0,0,0.6),
                0 0 40px rgba(139, 92, 246, 0.05);
            backdrop-filter:blur(25px);
            animation:cardIn .6s cubic-bezier(0.16, 1, 0.3, 1) both;
        }
        @keyframes cardIn {
            from { opacity:0; transform:translateY(30px) scale(.95); }
            to   { opacity:1; transform:translateY(0) scale(1); }
        }

        /* Error icon */
        .err-icon {
            width:72px; height:72px; border-radius:50%;
            margin:0 auto 1.5rem;
            background:var(--err2);
            border:1px solid rgba(244, 63, 94, 0.25);
            display:flex; align-items:center; justify-content:center;
            box-shadow: 0 0 25px rgba(244, 63, 94, 0.15);
        }
        .err-icon svg { color:var(--err); }

        .err-label {
            font-size:0.7rem; font-weight:800; letter-spacing:0.15em;
            text-transform:uppercase; color:var(--err); margin-bottom:0.7rem;
        }
        .error-card h2 {
            font-size:1.7rem; font-weight:800; letter-spacing:-0.03em;
            margin-bottom:0.75rem; color: #fff;
        }
        .error-card p {
            font-size:0.9rem; color:var(--txt2); line-height:1.6;
            margin-bottom:2rem; font-weight: 500;
        }

        /* Buttons */
        .err-btns { display:flex; flex-direction:column; gap:0.8rem; width:100%; align-items:center; }
        .ebtn {
            display:flex; align-items:center; justify-content:center; gap:0.6rem;
            width:100%; max-width:300px;
            padding:1rem 1.5rem; border-radius:14px;
            font-family:inherit; font-size:0.85rem; font-weight:700;
            cursor:pointer; text-decoration:none; color:#fff; border:none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: linear-gradient(135deg, var(--p2), var(--p));
            box-shadow: 0 8px 20px rgba(124, 58, 237, 0.25);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .ebtn:hover {
            transform:translateY(-3px);
            box-shadow: 0 12px 25px rgba(124, 58, 237, 0.4);
            filter:brightness(1.1);
        }
        .ebtn:active { transform:scale(.97); }

        /* Footer */
        footer {
            padding:1.5rem; text-align:center;
            color:var(--txt2); font-size:0.7rem;
            letter-spacing: 0.02em;
        }
        footer::before {
            content:''; display:block;
            width:60px; height:1px;
            background:linear-gradient(90deg,transparent,rgba(139, 92, 246, 0.3),transparent);
            margin:0 auto 1rem;
        }
        .ha-link {
            color:var(--p); text-decoration:none; font-weight:700;
            transition:opacity .2s;
        }
        .ha-link:hover { opacity:.8; text-decoration: underline; }
    </style>
</head>
<body>

<header>
    <span class="header-logo">ɪɴꜰɪɴɪᴛʏ ʙᴏᴛᴢ</span>
</header>

<main>
  <div class="error-card">

    <div class="err-icon">
      <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
    </div>

    <div class="err-label">sʏsᴛᴇᴍ ᴇʀʀᴏʀ</div>
    <h2>Something went wrong</h2>
    <p>We couldn't load this file. It may have expired, been removed, or there's a temporary database issue.</p>

    <div class="err-btns">
      <button class="ebtn" onclick="location.reload()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
        Try Again
      </button>
      <a href="https://t.me/infinity_botzz" class="ebtn" target="_blank" rel="noopener">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
        Support Group
      </a>
    </div>

  </div>
</main>

<footer>
  <p>ᴘᴏᴡᴇʀᴇᴅ ʙʏ <a href="https://t.me/infinity_botzz" class="ha-link" target="_blank" rel="noopener">ɪɴꜰɪɴɪᴛʏ ʙᴏᴛᴢ</a></p>
</footer>
</body>
</html>
"""

# ─────────────────────────────────────────────────────────────────────────────
# 5. NO TMDB KEY PAGE TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────
no_tmdb_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebApp Unavailable</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * { box-sizing:border-box; margin:0; padding:0; }
        body {
            font-family:'Outfit',sans-serif; background:#0a0a0f; color:#fff;
            min-height:100vh; display:flex; align-items:center; justify-content:center;
            padding:30px 24px; text-align:center;
            background-image: radial-gradient(ellipse at 50% 0%, rgba(229,9,20,0.08) 0%, transparent 60%);
        }
        .wrap { max-width:380px; }
        .icon {
            width:90px; height:90px; border-radius:24px; margin:0 auto 28px;
            background:linear-gradient(135deg,#1a1a2e,#16213e);
            border:1px solid rgba(229,9,20,0.3);
            display:flex; align-items:center; justify-content:center; font-size:40px;
            box-shadow: 0 0 40px rgba(229,9,20,0.1);
        }
        h1 { font-size:26px; font-weight:800; margin-bottom:12px; letter-spacing:-0.5px; }
        p { font-size:15px; color:#888; line-height:1.7; }
        code {
            display:inline-block; background:#1e1e2a; color:#e50914;
            padding:3px 10px; border-radius:6px; font-size:14px;
            border:1px solid rgba(229,9,20,0.25); margin:4px 0;
            font-family:monospace;
        }
        .divider {
            width:60px; height:2px; background:linear-gradient(90deg,transparent,#e50914,transparent);
            margin:24px auto;
        }
        .note { font-size:12px; color:#444; margin-top:16px; }
    </style>
</head>
<body>
<div class="wrap">
    <div class="icon">🔑</div>
    <h1>WebApp Unavailable</h1>
    <div class="divider"></div>
    <p>The WebApp requires a <b>TMDB API Key</b> to function.</p>
    <p style="margin-top:12px">If you're an admin, set the environment variable:</p>
    <p style="margin-top:10px"><code>TMDB_API_KEY</code></p>
    <p style="margin-top:14px; color:#555">Get your free API key at<br><span style="color:#e50914">themoviedb.org/settings/api</span></p>
    <div class="note">This message is only shown when the key is not configured.</div>
</div>
<script>
    const tg = window.Telegram?.WebApp;
    if (tg) { tg.expand(); tg.setBackgroundColor('#0a0a0f'); }
</script>
</body>
</html>
"""

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