"""
Exemplo com proxy autenticado
-------------------------------
Demonstra como usar proxy com usuario e senha no modo stealth.

Dois formatos disponiveis:
  - sync_com_proxy(): usa sb_cdp (formato sync leve)
  - async_com_proxy(): usa cdp_driver (formato async)

Substitua as variaveis PROXY_USER, PROXY_PASS, PROXY_HOST, PROXY_PORT
e TARGET_URL com os seus valores reais antes de executar.

Uso: python exemplo_com_proxy.py
"""

import asyncio
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from seleniumbase import sb_cdp, cdp_driver

# Configuracoes do proxy — substitua com seus dados reais
PROXY_USER = "usuario"
PROXY_PASS = "senha"
PROXY_HOST = "servidor"
PROXY_PORT = "porta"
PROXY = f"{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"

TARGET_URL = "https://example.com"


def sync_com_proxy():
    """Formato sync leve com proxy autenticado."""
    # use_chromium=True e necessario para suporte a extensao de autenticacao de proxy
    sb = sb_cdp.Chrome(use_chromium=True, proxy=PROXY)

    # Abre a URL antes de conectar o Playwright para que o proxy seja aplicado
    sb.open(TARGET_URL)
    endpoint_url = sb.get_endpoint_url()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(endpoint_url)
        page = browser.contexts[0].pages[0]

        titulo = page.title()
        print(f"[SYNC] Titulo: {titulo}")
        print(f"[SYNC] URL: {page.url}")


async def async_com_proxy():
    """Formato async com proxy autenticado."""
    driver = await cdp_driver.start_async(use_chromium=True, proxy=PROXY)

    # Abre a URL antes de conectar o Playwright para que o proxy seja aplicado
    await driver.get(TARGET_URL)
    endpoint_url = driver.get_endpoint_url()

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(endpoint_url)
        page = browser.contexts[0].pages[0]

        titulo = await page.title()
        print(f"[ASYNC] Titulo: {titulo}")
        print(f"[ASYNC] URL: {page.url}")


if __name__ == "__main__":
    print("=== Formato Sync com Proxy ===")
    sync_com_proxy()

    print("\n=== Formato Async com Proxy ===")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(async_com_proxy())
