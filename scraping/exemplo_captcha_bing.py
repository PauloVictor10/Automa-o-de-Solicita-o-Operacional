"""
Exemplo pratico: Resolucao de CAPTCHA no Bing
-----------------------------------------------
Demonstra como usar o modo stealth para contornar e resolver
o CAPTCHA do Bing automaticamente.

Usa o formato sb_cdp (sync leve) — sem WebDriver.

Uso: python exemplo_captcha_bing.py
"""

from playwright.sync_api import sync_playwright
from seleniumbase import sb_cdp

# Inicia Chrome em modo stealth com locale em ingles (necessario para o Bing)
sb = sb_cdp.Chrome(locale="en")
endpoint_url = sb.get_endpoint_url()

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(endpoint_url)
    page = browser.contexts[0].pages[0]

    # Acessa a pagina de CAPTCHA do Bing
    page.goto("https://www.bing.com/turing/captcha/challenge")
    page.wait_for_timeout(2000)

    # SeleniumBase resolve o CAPTCHA automaticamente
    sb.solve_captcha()
    page.wait_for_timeout(2000)

    print("CAPTCHA resolvido com sucesso!")
    print(f"URL atual: {page.url}")
