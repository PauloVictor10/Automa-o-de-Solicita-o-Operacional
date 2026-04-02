"""
Formato 2: SB() (sync completo)
--------------------------------
Melhor para projetos hibridos onde voce precisa alternar entre as APIs
do WebDriver e do Playwright na mesma sessao.

Acesso a todas as APIs: Selenium, SeleniumBase, UC Mode, CDP Mode e Playwright.

Uso: python formato_sync_completo.py
"""

from playwright.sync_api import sync_playwright
from seleniumbase import SB

with SB(uc=True) as sb:
    # Ativa o modo CDP para obter a URL de endpoint
    sb.activate_cdp_mode()
    endpoint_url = sb.cdp.get_endpoint_url()

    with sync_playwright() as p:
        # Playwright se conecta ao navegador stealth via CDP
        browser = p.chromium.connect_over_cdp(endpoint_url)
        page = browser.contexts[0].pages[0]

        page.goto("https://example.com")
        page.wait_for_timeout(2000)

        # Exemplo de uso combinado: Playwright para navegar, SeleniumBase para CAPTCHA
        titulo = page.title()
        print(f"Titulo da pagina: {titulo}")

        # sb.solve_captcha() pode ser chamado aqui se necessario
        # page.wait_for_selector("algum-seletor")

        conteudo = page.locator("body").inner_text()
        print(f"\nConteudo:\n{conteudo[:500]}")
