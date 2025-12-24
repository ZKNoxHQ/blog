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
            <a href="https://zknox.com/technologies.html" class="nav-link">Technologies</a>
            <a href="https://zknox.com/products.html" class="nav-link">Products</a>
            <a href="$root/index.html" class="nav-link active">Blog</a>
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
/* ZKNOX Navigation */
.zknox-nav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    background: #0a0a0f;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 16px;
}

.zknox-nav .nav-container {
    max-width: 1140px;
    margin: 0 auto;
    padding: 0 2rem;
    height: 70px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.zknox-nav .logo {
    display: flex;
    align-items: center;
    text-decoration: none;
}

.zknox-nav .logo img {
    height: 40px;
    width: auto;
}

.zknox-nav .nav-links {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.zknox-nav .nav-link {
    color: #a78bfa;
    text-decoration: none;
    padding: 0.5rem 1rem;
    font-size: 16px;
    font-weight: 500;
    font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif;
    border-radius: 6px;
    transition: all 0.2s ease;
}

.zknox-nav .nav-link:hover {
    color: #c4b5fd;
    background: rgba(167, 139, 250, 0.1);
}

.zknox-nav .nav-link.active {
    color: #c4b5fd;
}

.zknox-nav .nav-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    padding: 0;
}

.zknox-nav .nav-icon svg {
    width: 20px;
    height: 20px;
}

.zknox-nav .github-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1.2rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    color: #ffffff;
    text-decoration: none;
    font-size: 15px;
    font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif;
    font-weight: 500;
    transition: all 0.2s ease;
}

.zknox-nav .github-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: #a78bfa;
}

.zknox-nav .github-btn svg {
    width: 20px;
    height: 20px;
}

.zknox-nav .mobile-menu-btn {
    display: none;
    flex-direction: column;
    gap: 5px;
    padding: 0.5rem;
    background: none;
    border: none;
    cursor: pointer;
}

.zknox-nav .mobile-menu-btn span {
    width: 24px;
    height: 2px;
    background: #ffffff;
    transition: all 0.3s ease;
}

/* Add padding to body to account for fixed nav */
body {
    padding-top: 70px;
    font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 16px;
}

/* Mobile responsive */
@media (max-width: 900px) {
    .zknox-nav .nav-links {
        display: none;
        position: absolute;
        top: 70px;
        left: 0;
        right: 0;
        background: #0a0a0f;
        flex-direction: column;
        padding: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .zknox-nav .nav-links.active {
        display: flex;
    }

    .zknox-nav .nav-link {
        width: 100%;
        padding: 0.75rem 1rem;
    }

    .zknox-nav .mobile-menu-btn {
        display: flex;
    }

    .zknox-nav .github-btn {
        display: none;
    }
}
</style>
"""

ZKNOX_NAV_JS = """
<script>
function toggleMenu() {
    document.querySelector('.zknox-nav .nav-links').classList.toggle('active');
}
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
