"""
Formato 3: cdp_driver (async)
------------------------------
Projetado para Python assincrono moderno.
Permite rodar multiplas sessoes stealth concorrentes com async/await
e a async_api do Playwright.

Melhor para performance — asyncio gerencia tarefas nao bloqueantes.
Nao usa WebDriver.

Uso: python formato_async.py
"""

import asyncio
from seleniumbase import cdp_driver
from playwright.async_api import async_playwright


async def main():
    # Inicia o driver CDP assincrono (sem WebDriver)
    driver = await cdp_driver.start_async()
    endpoint_url = driver.get_endpoint_url()

    async with async_playwright() as p:
        # Playwright se conecta ao navegador stealth via CDP
        browser = await p.chromium.connect_over_cdp(endpoint_url)
        page = browser.contexts[0].pages[0]

        await page.goto("https://example.com")
        await page.wait_for_timeout(2000)

        titulo = await page.title()
        print(f"Titulo da pagina: {titulo}")

        conteudo = await page.locator("body").inner_text()
        print(f"\nConteudo:\n{conteudo[:500]}")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
