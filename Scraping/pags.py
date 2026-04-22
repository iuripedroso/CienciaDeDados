#!/usr/bin/env python3
"""
scrape_locomotive.py  —  Locomotive.ca full site ripper
========================================================
Usa Playwright (Chrome headless) para:
  • Renderizar o JS completo
  • Interceptar CADA requisição de rede (CSS, JS, imagens, fontes, vídeos)
  • Fazer scroll automático para disparar lazy-load
  • Salvar tudo localmente e reescrever o HTML com paths relativos

INSTALAÇÃO (uma vez só):
    pip install playwright beautifulsoup4 lxml
    playwright install chromium

USO:
    python scrape_locomotive.py

RESULTADO:
    ./locomotive_site/index.html   ← abre direto no browser (offline)
"""

import os
import re
import time
import mimetypes
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

# ── tenta importar dependências ──────────────────────────────────────────────
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌  Playwright não encontrado.")
    print("    Instale com:  pip install playwright && playwright install chromium")
    raise SystemExit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("❌  beautifulsoup4 não encontrado.")
    print("    Instale com:  pip install beautifulsoup4 lxml")
    raise SystemExit(1)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
BASE_URL   = "https://locomotive.ca/en"
OUTPUT_DIR = Path("./locomotive_site")

# Páginas internas para visitar
EXTRA_PAGES = [
    "https://locomotive.ca/en/work",
    "https://locomotive.ca/en/agency",
    "https://locomotive.ca/en/careers",
]

# Domínios cujos assets salvamos (CDN, fontes, etc.)
ALLOWED_ASSET_DOMAINS = {
    "locomotive.ca",
    "cdn.locomotive.ca",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "use.typekit.net",
    "p.typekit.net",
}

SCROLL_PAUSE = 0.4   # segundos entre scrolls
SCROLL_STEPS = 14    # quantos scrolls
WAIT_AFTER   = 3     # espera extra no final

# ─────────────────────────────────────────────────────────────────────────────
# ESTADO GLOBAL
# ─────────────────────────────────────────────────────────────────────────────
captured: dict[str, bytes] = {}   # url → bytes
mime_map: dict[str, str]   = {}   # url → content-type


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def ext_for(url: str, ct: str) -> str:
    path_ext = Path(urlparse(url).path).suffix.lower()
    if path_ext and path_ext not in (".php", ".aspx", ".ashx", ""):
        return path_ext
    raw = mimetypes.guess_extension(ct.split(";")[0].strip()) or ""
    fixes = {".jpe": ".jpg", ".jfif": ".jpg", ".jpeg": ".jpg"}
    return fixes.get(raw, raw) or ".bin"


def url_to_local(url: str, base_dir: Path, ext_override: str = "") -> Path:
    p    = urlparse(url)
    path = unquote(p.path).lstrip("/")
    if not path or path.endswith("/"):
        path = path.rstrip("/") + "/index"
    local = base_dir / p.netloc / path
    if ext_override and local.suffix != ext_override:
        local = local.with_suffix(ext_override)
    elif local.suffix == "":
        local = local.with_suffix(".html")
    return local


def rel_path(src: Path, dst: Path) -> str:
    try:
        return os.path.relpath(dst, src.parent).replace("\\", "/")
    except ValueError:
        return dst.as_posix()


def save_asset(url: str, data: bytes, ct: str) -> Path:
    ext   = ext_for(url, ct)
    local = url_to_local(url, OUTPUT_DIR, ext)
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_bytes(data)
    return local


def process_css(css_text: str, css_url: str, css_local: Path) -> str:
    """Reescreve url(...) dentro de CSS para paths relativos."""
    pattern = re.compile(r'url\(\s*["\']?([^)"\']+)["\']?\s*\)', re.IGNORECASE)

    def replace(m):
        raw = m.group(1).strip()
        if raw.startswith(("data:", "#")):
            return m.group(0)
        abs_url = urljoin(css_url, raw)
        if abs_url in captured:
            ct    = mime_map.get(abs_url, "application/octet-stream")
            asset = save_asset(abs_url, captured[abs_url], ct)
            return f'url("{rel_path(css_local, asset)}")'
        return m.group(0)

    return pattern.sub(replace, css_text)


# ─────────────────────────────────────────────────────────────────────────────
# INTERCEPT DE REDE
# ─────────────────────────────────────────────────────────────────────────────

def on_response(response):
    url = response.url
    if url.startswith(("data:", "blob:")):
        return
    domain = urlparse(url).netloc
    if any(domain == d or domain.endswith("." + d) for d in ALLOWED_ASSET_DOMAINS):
        try:
            body = response.body()
            ct   = response.headers.get("content-type", "application/octet-stream")
            captured[url] = body
            mime_map[url] = ct
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# NAVEGAÇÃO + SCROLL
# ─────────────────────────────────────────────────────────────────────────────

def scrape_page(page, url: str) -> str:
    print(f"  🌐 abrindo  {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=45_000)

    # Scroll progressivo
    height = page.evaluate("document.body.scrollHeight")
    step   = max(height // SCROLL_STEPS, 400)
    pos    = 0
    while pos < height:
        pos += step
        page.evaluate(f"window.scrollTo(0, {pos})")
        time.sleep(SCROLL_PAUSE)
        height = page.evaluate("document.body.scrollHeight")

    page.evaluate("window.scrollTo(0, 0)")
    try:
        page.wait_for_load_state("networkidle", timeout=10_000)
    except Exception:
        pass
    time.sleep(WAIT_AFTER)

    return page.content()


# ─────────────────────────────────────────────────────────────────────────────
# REESCRITA DO HTML
# ─────────────────────────────────────────────────────────────────────────────

def rewrite_html(html: str, page_url: str) -> str:
    soup       = BeautifulSoup(html, "lxml")
    page_local = url_to_local(page_url, OUTPUT_DIR, ".html")

    def resolve(raw: str):
        raw = (raw or "").strip()
        if not raw or raw.startswith(("data:", "blob:", "javascript:", "mailto:", "tel:", "#")):
            return None
        return urljoin(page_url, raw)

    def asset_rel(abs_url: str):
        if abs_url not in captured:
            return None
        ct    = mime_map.get(abs_url, "application/octet-stream")
        local = save_asset(abs_url, captured[abs_url], ct)
        return rel_path(page_local, local)

    # <link href>
    for tag in soup.find_all("link", href=True):
        abs_url = resolve(tag["href"])
        if not abs_url:
            continue
        r = asset_rel(abs_url)
        if r:
            tag["href"] = r
            # Reprocessa CSS interno
            css_local = url_to_local(abs_url, OUTPUT_DIR, ".css")
            if css_local.exists():
                try:
                    txt = css_local.read_text(encoding="utf-8", errors="replace")
                    css_local.write_text(process_css(txt, abs_url, css_local), encoding="utf-8")
                except Exception:
                    pass

    # <script src>
    for tag in soup.find_all("script", src=True):
        abs_url = resolve(tag["src"])
        if abs_url:
            r = asset_rel(abs_url)
            if r:
                tag["src"] = r

    # <img>
    for tag in soup.find_all("img"):
        for attr in ("src", "data-src", "data-lazy-src", "data-original", "data-bg"):
            raw = tag.get(attr)
            if raw and not raw.startswith("data:"):
                abs_url = resolve(raw)
                if abs_url:
                    r = asset_rel(abs_url)
                    if r:
                        tag[attr] = r
        # srcset
        srcset = tag.get("srcset", "")
        if srcset:
            parts = []
            for chunk in srcset.split(","):
                tokens = chunk.strip().split()
                if tokens:
                    abs_url = resolve(tokens[0])
                    if abs_url:
                        r = asset_rel(abs_url)
                        if r:
                            tokens[0] = r
                    parts.append(" ".join(tokens))
            tag["srcset"] = ", ".join(parts)

    # <source>
    for tag in soup.find_all("source"):
        for attr in ("src", "srcset"):
            raw = tag.get(attr)
            if raw:
                abs_url = resolve(raw)
                if abs_url:
                    r = asset_rel(abs_url)
                    if r:
                        tag[attr] = r

    # <video poster>
    for tag in soup.find_all("video", poster=True):
        abs_url = resolve(tag["poster"])
        if abs_url:
            r = asset_rel(abs_url)
            if r:
                tag["poster"] = r

    # style= inline + <style> blocks
    for tag in soup.find_all(style=True):
        tag["style"] = process_css(tag["style"], page_url, page_local)
    for tag in soup.find_all("style"):
        if tag.string:
            tag.string.replace_with(process_css(tag.string, page_url, page_local))

    return str(soup)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("🚂  Locomotive scraper — Playwright edition")
    print(f"    Destino : {OUTPUT_DIR.resolve()}\n")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pages_to_visit = [BASE_URL] + EXTRA_PAGES
    visited        = set()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
            locale="en-US",
        )
        page = context.new_page()
        page.on("response", on_response)

        for url in pages_to_visit:
            if url in visited:
                continue
            visited.add(url)
            print(f"\n📄 Página: {url}")

            try:
                html = scrape_page(page, url)

                # Descobre novas páginas internas
                soup = BeautifulSoup(html, "lxml")
                for a in soup.find_all("a", href=True):
                    abs_href = urljoin(url, a["href"]).split("?")[0].split("#")[0]
                    if (abs_href.startswith("https://locomotive.ca/en")
                            and abs_href not in visited
                            and abs_href not in pages_to_visit
                            and not Path(urlparse(abs_href).path).suffix):
                        pages_to_visit.append(abs_href)
                        print(f"     ➕ descoberta: {abs_href}")

                new_html   = rewrite_html(html, url)
                local_file = url_to_local(url, OUTPUT_DIR, ".html")
                local_file.parent.mkdir(parents=True, exist_ok=True)
                local_file.write_text(new_html, encoding="utf-8")
                print(f"   ✅ {local_file}  ({len(captured)} recursos capturados até agora)")

            except Exception as e:
                print(f"   ❌ erro: {e}")

        browser.close()

    # Relatório
    print("\n" + "─" * 60)
    all_files   = [f for f in OUTPUT_DIR.rglob("*") if f.is_file()]
    total_bytes = sum(f.stat().st_size for f in all_files)
    by_ext: dict[str, int] = {}
    for f in all_files:
        e = f.suffix.lower() or "outro"
        by_ext[e] = by_ext.get(e, 0) + 1

    print(f"✅  {len(all_files)} arquivos  |  {total_bytes/1024:.0f} KB  ({total_bytes/1024**2:.1f} MB)")
    print("\n📊 Por tipo:")
    for ext, n in sorted(by_ext.items(), key=lambda x: -x[1]):
        print(f"   {ext:>8}  →  {n}")

    index = OUTPUT_DIR / "locomotive.ca" / "en" / "index.html"
    if index.exists():
        print(f"\n🌍 Abra no browser:\n   file://{index.resolve()}")
    print("─" * 60)


if __name__ == "__main__":
    main()