"""
Formato 1: sb_cdp (sync leve)
-------------------------------
Ideal para scripts independentes que usam principalmente Playwright,
mas precisam do modo stealth do SeleniumBase para contornar deteccao de bots
e resolver CAPTCHAs sem a sobrecarga do WebDriver.

Uso: python formato_sync_leve.py
"""

from playwright.sync_api import sync_playwright
from seleniumbase import sb_cdp

# Inicia o Chrome em modo stealth (sem WebDriver)
sb = sb_cdp.Chrome()
endpoint_url = sb.get_endpoint_url()

with sync_playwright() as p:
    # Playwright se conecta ao navegador stealth via CDP
    browser = p.chromium.connect_over_cdp(endpoint_url)
    page = browser.contexts[0].pages[0]

    page.goto("https://example.com")
    page.wait_for_timeout(2000)

    titulo = page.title()
    print(f"Titulo da pagina: {titulo}")

    conteudo = page.locator("body").inner_text()
    print(f"\nConteudo:\n{conteudo[:500]}")
