#!/usr/bin/python3
import os, sys, datetime

PRE_HEADER = """

<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Source+Sans+3:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
@media (prefers-color-scheme: dark) {
    body {
        background-color: #0a0a0f;
        color: white;
    }
    .markdown-body table tr {
        background-color: #0a0a0f;
    }
    .markdown-body table tr:nth-child(2n) {
        background-color: #12121a;
    }
}
</style>
</head>
<body>

"""

ZKNOX_NAV_BANNER = """
<!-- ZKNOX Navigation Banner -->
<nav class="zknox-nav">
    <div class="nav-container">
        <a href="https://zknox.com" class="logo">
            <img src="$root/images/zknox-logo.png" alt="ZKNOX">
        </a>
        
        <div class="nav-links">
            <a href="https://zknox.com" class="nav-link">Home</a>
            
            <div class="nav-dropdown">
                <a href="https://zknox.com/technologies.html" class="nav-link">Technologies</a>
                <div class="dropdown-menu">
                    <a href="https://zknox.com/tech-ecc.html" class="dropdown-item">Elliptic Curves</a>
                    <a href="https://zknox.com/tech-hw.html" class="dropdown-item">Hardware Wallets</a>
                    <a href="https://zknox.com/tech-mpc.html" class="dropdown-item">MPC</a>
                    <a href="https://zknox.com/tech-pqc.html" class="dropdown-item">Post-Quantum Cryptography</a>
                    <a href="https://zknox.com/tech-zk.html" class="dropdown-item">Zero Knowledge</a>
                </div>
            </div>
            
            <div class="nav-dropdown">
                <a href="https://zknox.com/products.html" class="nav-link">Products</a>
                <div class="dropdown-menu">
                    <a href="https://zknox.com/products.html#libraries" class="dropdown-item">Cryptographic Libraries</a>
                    <a href="https://zknox.com/products.html#hardware" class="dropdown-item">Hardware Integration</a>
                    <a href="https://zknox.com/products.html#contracts" class="dropdown-item">Smart Contracts</a>
                    <a href="https://zknox.com/products.html#zk" class="dropdown-item">ZK Circuits</a>
                </div>
            </div>
            
            <div class="nav-dropdown">
                <a href="https://zknox.com/tools.html" class="nav-link">Tools</a>
                <div class="dropdown-menu">
                    <a href="https://zknox.com/demo-pqbip39.html" class="dropdown-item">PQBIP39</a>
                    <a href="https://zknox.com/zknox-account.html" class="dropdown-item">ZKNOX Account</a>
                    <a href="https://zknox.com/zknox-blue/official-apps.html" class="dropdown-item">ZKNOX Blue</a>
                    <a href="https://zknox.com/zknox-orange/sideloader.html" class="dropdown-item">ZKNOX Orange</a>
                    <a href="https://zknox.com/demo-zk-hardware.html" class="dropdown-item">ZK-Hardware</a>
                    <a href="https://zknox.com/faucet.html" class="dropdown-item">Faucet</a>
                </div>
            </div>
            
            <div class="nav-dropdown">
                <a href="https://zknox.com/research.html" class="nav-link">Research</a>
                <div class="dropdown-menu">
                    <a href="$root/index.html" class="dropdown-item">Blog</a>
                    <a href="https://zknox.com/eips.html" class="dropdown-item">EIPs</a>
                    <a href="https://zknox.com/hackathons.html" class="dropdown-item">Hackathons</a>
                    <a href="https://zknox.com/papers.html" class="dropdown-item">Papers</a>
                    <a href="https://zknox.com/talks.html" class="dropdown-item">Talks</a>
                </div>
            </div>
            
            <div class="nav-dropdown">
                <a href="https://zknox.com/services.html" class="nav-link">Services</a>
                <div class="dropdown-menu">
                    <a href="https://zknox.com/services.html#audits" class="dropdown-item">Audits</a>
                    <a href="https://zknox.com/services.html#design" class="dropdown-item">Design</a>
                    <a href="https://zknox.com/services.html#hardware" class="dropdown-item">Hardware Integration</a>
                    <a href="https://zknox.com/services.html#implementation" class="dropdown-item">Implementation</a>
                </div>
            </div>
            
            <a href="https://zknox.com/team.html" class="nav-link">Team</a>
            <a href="https://x.com/zknoxHQ" class="nav-link nav-icon" target="_blank" title="X/Twitter">
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
            </a>
        </div>

        <a href="https://github.com/ZKNoxHQ" class="github-btn" target="_blank">
            <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub
        </a>

        <button class="mobile-menu-btn" onclick="toggleMenu()">
            <span></span>
            <span></span>
            <span></span>
        </button>
    </div>
</nav>
<!-- End ZKNOX Navigation Banner -->
"""

ZKNOX_NAV_CSS = """
<style>
/* ZKNOX Navigation - Reset and Override */
.zknox-nav,
.zknox-nav * {
    box-sizing: border-box !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.6 !important;
}

.zknox-nav {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 1000 !important;
    background: #0a0a0f !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    font-size: 16px !important;
    font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.zknox-nav .nav-container {
    max-width: 1140px !important;
    margin: 0 auto !important;
    padding: 0 32px !important;
    height: 70px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
}

.zknox-nav .logo {
    display: flex !important;
    align-items: center !important;
    text-decoration: none !important;
    padding: 0 !important;
}

.zknox-nav .logo img {
    height: 48px !important;
    width: auto !important;
}

.zknox-nav .nav-links {
    display: flex !important;
    align-items: center !important;
    gap: 4px !important;
}

.zknox-nav .nav-link {
    color: #a78bfa !important;
    text-decoration: none !important;
    padding: 8px 16px !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif !important;
    border-radius: 6px !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
    background: transparent !important;
    border: none !important;
}

.zknox-nav .nav-link:hover {
    color: #c4b5fd !important;
    background: rgba(167, 139, 250, 0.1) !important;
}

.zknox-nav .nav-link.active {
    color: #c4b5fd !important;
}

/* Dropdown Navigation */
.zknox-nav .nav-dropdown {
    position: relative !important;
    display: flex !important;
}

.zknox-nav .nav-dropdown > .nav-link {
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
}

.zknox-nav .nav-dropdown > .nav-link::after {
    content: '' !important;
    width: 0 !important;
    height: 0 !important;
    border-left: 4px solid transparent !important;
    border-right: 4px solid transparent !important;
    border-top: 4px solid currentColor !important;
    transition: transform 0.2s ease !important;
}

.zknox-nav .nav-dropdown:hover > .nav-link::after {
    transform: rotate(180deg) !important;
}

.zknox-nav .dropdown-menu {
    position: absolute !important;
    top: 100% !important;
    left: 0 !important;
    min-width: 220px !important;
    background: #1a1a25 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    padding: 8px !important;
    opacity: 0 !important;
    visibility: hidden !important;
    transform: translateY(10px) !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3) !important;
    display: block !important;
}

.zknox-nav .nav-dropdown:hover .dropdown-menu {
    opacity: 1 !important;
    visibility: visible !important;
    transform: translateY(5px) !important;
}

.zknox-nav .dropdown-item {
    display: block !important;
    padding: 10px 16px !important;
    color: #9ca3af !important;
    text-decoration: none !important;
    font-size: 14px !important;
    font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif !important;
    border-radius: 6px !important;
    transition: all 0.2s ease !important;
    background: transparent !important;
}

.zknox-nav .dropdown-item:hover {
    color: #a78bfa !important;
    background: rgba(167, 139, 250, 0.1) !important;
}

.zknox-nav .nav-icon {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 40px !important;
    padding: 8px 0 !important;
}

.zknox-nav .nav-icon svg {
    width: 18px !important;
    height: 18px !important;
}

.zknox-nav .github-btn {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    padding: 8px 16px !important;
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    text-decoration: none !important;
    font-size: 14px !important;
    font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.zknox-nav .github-btn:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    border-color: #a78bfa !important;
}

.zknox-nav .github-btn svg {
    width: 18px !important;
    height: 18px !important;
}

.zknox-nav .mobile-menu-btn {
    display: none !important;
    flex-direction: column !important;
    gap: 5px !important;
    padding: 8px !important;
    background: none !important;
    border: none !important;
    cursor: pointer !important;
}

.zknox-nav .mobile-menu-btn span {
    width: 22px !important;
    height: 2px !important;
    background: #ffffff !important;
    transition: all 0.3s ease !important;
    display: block !important;
}

/* Add padding to body to account for fixed nav */
body {
    padding-top: 70px !important;
}

/* Mobile responsive */
@media (max-width: 900px) {
    .zknox-nav .nav-links {
        display: none !important;
        position: absolute !important;
        top: 70px !important;
        left: 0 !important;
        right: 0 !important;
        background: #0a0a0f !important;
        flex-direction: column !important;
        padding: 16px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        max-height: calc(100vh - 70px) !important;
        overflow-y: auto !important;
        gap: 0 !important;
    }

    .zknox-nav .nav-links.active {
        display: flex !important;
    }

    .zknox-nav .nav-link {
        width: 100% !important;
        padding: 12px 16px !important;
    }

    /* Accordéon mobile */
    .zknox-nav .nav-dropdown {
        flex-direction: column !important;
        width: 100% !important;
    }

    .zknox-nav .nav-dropdown > .nav-link {
        justify-content: space-between !important;
        width: 100% !important;
    }

    .zknox-nav .nav-dropdown > .nav-link::after {
        transition: transform 0.3s ease !important;
    }

    .zknox-nav .nav-dropdown.open > .nav-link::after {
        transform: rotate(180deg) !important;
    }

    .zknox-nav .dropdown-menu {
        position: static !important;
        opacity: 1 !important;
        visibility: visible !important;
        transform: none !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 0 0 16px !important;
        display: none !important;
        max-height: 0 !important;
        overflow: hidden !important;
        min-width: auto !important;
    }

    .zknox-nav .nav-dropdown.open .dropdown-menu {
        display: block !important;
        max-height: 500px !important;
    }

    .zknox-nav .mobile-menu-btn {
        display: flex !important;
    }

    .zknox-nav .github-btn {
        display: none !important;
    }
}
</style>
"""

ZKNOX_NAV_JS = """
<script>
function toggleMenu() {
    document.querySelector('.zknox-nav .nav-links').classList.toggle('active');
}

// Accordéon mobile
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.zknox-nav .nav-dropdown > .nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            if (window.innerWidth <= 900) {
                e.preventDefault();
                const dropdown = this.parentElement;
                document.querySelectorAll('.zknox-nav .nav-dropdown.open').forEach(d => {
                    if (d !== dropdown) d.classList.remove('open');
                });
                dropdown.classList.toggle('open');
            }
        });
    });
});
</script>
"""

ZKNOX_FOOTER = """
<!-- ZKNOX Footer -->
<footer class="zknox-footer">
    <div class="footer-container">
        <p class="footer-copy">Copyright © 2025 <a href="https://zknox.com">ZKNOX</a> All rights reserved.</p>
    </div>
</footer>
<style>
.zknox-footer {
    background: #0a0a0f;
    padding: 2rem;
    text-align: center;
    border-top: 1px solid rgba(167, 139, 250, 0.2);
    margin-top: 4rem;
}
.zknox-footer .footer-copy {
    color: #a78bfa;
    font-size: 15px;
    margin: 0;
    font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif;
}
.zknox-footer .footer-copy a {
    color: #ffffff;
    text-decoration: none;
    font-weight: 600;
}
.zknox-footer .footer-copy a:hover {
    color: #c4b5fd;
}
</style>
"""

HEADER_TEMPLATE = """

<link rel="stylesheet" type="text/css" href="$root/css/common-vendor.b8ecfc406ac0b5f77a26.css">
<link rel="stylesheet" type="text/css" href="$root/css/fretboard.f32f2a8d5293869f0195.css">
<link rel="stylesheet" type="text/css" href="$root/css/pretty.0ae3265014f89d9850bf.css">
<link rel="stylesheet" type="text/css" href="$root/css/pretty-vendor.83ac49e057c3eac4fce3.css">
<link rel="stylesheet" type="text/css" href="$root/css/global.css">
<link rel="stylesheet" type="text/css" href="$root/css/misc.css">

<script type="text/x-mathjax-config">
<script>
MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']]
  },
  svg: {
    fontCache: 'global',
  }
};
</script>
<script type="text/javascript" id="MathJax-script" async
  src="$root/scripts/tex-svg.js">
</script>

<style>
</style>

<div id="doc" class="container-fluid markdown-body comment-enabled" data-hard-breaks="true">

<div id="color-mode-switch">
  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
    <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
  </svg>
  <input type="checkbox" id="switch" />
  <label for="switch">Dark Mode Toggle</label>
  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
    <path stroke-linecap="round" stroke-linejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
  </svg>
</div>
"""

TOGGLE_COLOR_SCHEME_JS = """
<script type="text/javascript">
  // Update root html class to set CSS colors
  const toggleDarkMode = () => {
    const root = document.querySelector('html');
    root.classList.toggle('dark');
  }

  // Update local storage value for colorScheme
  const toggleColorScheme = () => {
    const colorScheme = localStorage.getItem('colorScheme');
    if (colorScheme === 'light') localStorage.setItem('colorScheme', 'dark');
    else localStorage.setItem('colorScheme', 'light');
  }

  // Set toggle input handler
  const toggle = document.querySelector('#color-mode-switch input[type="checkbox"]');
  if (toggle) toggle.onclick = () => {
    toggleDarkMode();
    toggleColorScheme();
  }

  // Check for color scheme on init
  const checkColorScheme = () => {
    const colorScheme = localStorage.getItem('colorScheme');
    // Default to light for first view
    if (colorScheme === null || colorScheme === undefined) localStorage.setItem('colorScheme', 'light');
    // If previously saved to dark, toggle switch and update colors
    if (colorScheme === 'dark') {
      toggle.checked = true;
      toggleDarkMode();
    }
  }
  checkColorScheme();
</script>
"""

RSS_LINK = """

<link rel="alternate" type="application/rss+xml" href="{}/feed.xml" title="{}">

"""

TITLE_TEMPLATE = """

<br>
<h1 style="margin-bottom:7px"> {0} </h1>
<small style="float:left; color: #888"> {1} </small>
<small style="float:right; color: #888"><a href="{2}/index.html">See all posts</a></small>
<br> <br> <br>
<title> {0} </title>

"""

TOC_TITLE_TEMPLATE = """

<title> {0} </title>
<br>
<center><h1 style="border-bottom:0px"> {0} </h1></center>

"""

FOOTER = """ </div> """

TOC_START = """

<br>
<ul class="post-list" style="padding-left:0">

"""

TOC_END = """ </ul> """

TOC_ITEM_TEMPLATE = """

<li>
    <span class="post-meta">{}</span>
    <h3 style="margin-top:12px">
      <a class="post-link" href="{}">{}</a>
    </h3>
</li>

"""

TWITTER_CARD_TEMPLATE = """
<meta name="twitter:card" content="summary" />
<meta name="twitter:title" content="{}" />
<meta name="twitter:image" content="{}" />
"""


RSS_ITEM_TEMPLATE = """
<item>
<title>{title}</title>
<link>{link}</link>
<guid>{link}</guid>
<pubDate>{pub_date}</pubDate>
<description>{description}</description>
</item>
"""


RSS_MAIN_TEMPLATE = """
<?xml version="1.0" ?>
<rss version="2.0">
<channel>
  <title>{title}</title>
  <link>{link}</link>
  <description>{title}</description>
  <image>
      <url>{icon}</url>
      <title>{title}</title>
      <link>{link}</link>
  </image>
{items}
</channel>
</rss>
"""

def extract_metadata(fil, filename=None):
    metadata = {}
    if filename:
        assert filename[-3:] == '.md'
        metadata["filename"] = filename[:-3]+'.html'
    while 1:
        line = fil.readline()
        if line and line[0] == '[' and ']' in line:
            key = line[1:line.find(']')]
            value_start = line.find('(')+1
            value_end = line.rfind(')')
            if key in ('category', 'categories'):
                metadata['categories'] = set([
                    x.strip().lower() for x in line[value_start:value_end].split(',')
                ])
                assert '' not in metadata['categories']
            else:
                metadata[key] = line[value_start:value_end]
        else:
            break
    return metadata


def metadata_to_path(global_config, metadata):
    return os.path.join(
        global_config.get('posts_directory', 'posts'),
        metadata['date'],
        metadata['filename']
    )


def generate_feed(global_config, metadatas):
    def get_link(route):
        return global_config['domain'] + "/" + route

    def get_date(date_text):
        year, month, day = (int(x) for x in date_text.split('/'))
        date = datetime.date(year, month, day)
        return date.strftime('%a, %d %b %Y 00:00:00 +0000')

    def get_item(metadata):
        return RSS_ITEM_TEMPLATE.format(
            title=metadata['title'],
            link=get_link('/'.join([global_config['posts_directory'], metadata['date'], metadata['filename']])),
            pub_date=get_date(metadata['date']), description=''
        )

    return RSS_MAIN_TEMPLATE.strip().format(
        title=global_config['title'],
        link=get_link(''),
        icon=global_config['icon'],
        items="\n".join(map(get_item, metadatas))
    )




def make_twitter_card(title, global_config):
    return TWITTER_CARD_TEMPLATE.format(title, global_config['icon'])


def defancify(text):
    return text \
        .replace("'", "'") \
        .replace('"', '"') \
        .replace('"', '"') \
        .replace('…', '...') \


def make_categories_header(categories, root_path):
    o = ['<center><hr>']
    for category in categories:
        template = '<span class="toc-category" style="font-size:{}%"><a href="{}/categories/{}.html">{}</a></span>'
        o.append(template.format(min(100, 900 // len(category)), root_path, category, category.capitalize()))
    o.append('<hr></center>')
    return '\n'.join(o)


def get_printed_date(metadata):
    year, month, day = metadata['date'].split('/')
    month = 'JanFebMarAprMayJunJulAugSepOctNovDec'[int(month)*3-3:][:3]
    return year + ' ' + month + ' ' + day

def make_toc_item(global_config, metadata, root_path):
    link = metadata_to_path(global_config, metadata)
    return TOC_ITEM_TEMPLATE.format(get_printed_date(metadata), root_path + '/' + link, metadata['title'])


def make_toc(toc_items, global_config, all_categories, category=None):
    if category:
        title = category.capitalize()
        root_path = '..'
    else:
        title = global_config['title']
        root_path = '.'

    return (
        PRE_HEADER +
        ZKNOX_NAV_CSS +
        ZKNOX_NAV_BANNER.replace('$root', root_path) +
        RSS_LINK.format(root_path, title) +
        HEADER_TEMPLATE.replace('$root', root_path) +
        TOGGLE_COLOR_SCHEME_JS +
        make_twitter_card(title, global_config) +
        TOC_TITLE_TEMPLATE.format(title) +
        make_categories_header(all_categories, root_path) +
        TOC_START +
        ''.join(toc_items) +
        TOC_END +
        FOOTER +
        ZKNOX_FOOTER +
        ZKNOX_NAV_JS +
        '</body></html>'
    )


if __name__ == '__main__':
    # Get blog config
    global_config = extract_metadata(open('config.md'))

    # Special case: '--sync' option
    if '--sync' in sys.argv:
        os.system('rsync -av site/. {}:{}'.format(global_config['server'], global_config['website_root']))
        sys.exit()

    # Normal case: process each provided file
    for file_location in sys.argv[1:]:
        filename = os.path.split(file_location)[1]
        print("Processing file: {}".format(filename))

        # Extract path
        file_data = open(file_location).read()
        metadata = extract_metadata(open(file_location), filename)
        path = metadata_to_path(global_config, metadata)

        # Generate the html file
        options = metadata.get('pandoc', '')

        os.system('pandoc -o /tmp/temp_output.html {} {}'.format(file_location, options))
        root_path = '../../../..'
        total_file_contents = (
            PRE_HEADER +
            ZKNOX_NAV_CSS +
            ZKNOX_NAV_BANNER.replace('$root', root_path) +
            RSS_LINK.format(root_path, metadata['title']) +
            HEADER_TEMPLATE.replace('$root', root_path) +
            TOGGLE_COLOR_SCHEME_JS +
            make_twitter_card(metadata['title'], global_config) +
            TITLE_TEMPLATE.format(metadata['title'], get_printed_date(metadata), root_path) +
            defancify(open('/tmp/temp_output.html').read()) +
            FOOTER +
            ZKNOX_FOOTER +
            ZKNOX_NAV_JS +
            '</body></html>'
        )

        print("Path selected: {}".format(path))

        # Make sure target directory exists
        truncated_path = os.path.split(path)[0]
        os.system('mkdir -p {}'.format(os.path.join('site', truncated_path)))

        # Put it in the desired location
        out_location = os.path.join('site', path)
        open(out_location, 'w').write(total_file_contents)

    # Reset ToC
    metadatas = []
    categories = set()
    for filename in os.listdir('posts'):
        if filename[-4:-1] != '.sw':
            metadatas.append(extract_metadata(open(os.path.join('posts', filename)), filename))
            categories = categories.union(metadatas[-1]['categories'])
    categories = sorted(categories)

    print("Detected categories: {}".format(' '.join(categories)))

    sorted_metadatas = sorted(metadatas, key=lambda x: x['date'], reverse=True)
    feed = generate_feed(global_config, sorted_metadatas)

    os.system('mkdir -p {}'.format(os.path.join('site', 'categories')))

    print("Building tables of contents...")

    homepage_toc_items = [
        make_toc_item(global_config, metadata, '.') for metadata in sorted_metadatas if
        global_config.get('homepage_category', '') in metadata['categories'].union({''})
    ]

    for category in categories:
        category_toc_items = [
            make_toc_item(global_config, metadata, '..') for metadata in sorted_metadatas if
            category in metadata['categories']
        ]
        toc = make_toc(category_toc_items, global_config, categories, category)
        open(os.path.join('site', 'categories', category+'.html'), 'w').write(toc)

    open('site/feed.xml', 'w').write(feed)
    open('site/index.html', 'w').write(make_toc(homepage_toc_items, global_config, categories))

    # Copy CSS and scripts files
    this_file_directory = os.path.dirname(__file__)
    os.system('cp -r {} site/'.format(os.path.join(this_file_directory, 'css')))
    os.system('cp -r {} site/'.format(os.path.join(this_file_directory, 'scripts')))
    os.system('rsync -av images site/')
