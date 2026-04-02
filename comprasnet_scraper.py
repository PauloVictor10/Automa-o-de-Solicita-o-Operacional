import asyncio
import sys
from playwright.async_api import async_playwright
from anticaptchaofficial.hcaptchasolver import hCaptchaProxyless

# CONFIGURAÇÕES
API_KEY = "a4fbf1a6819f55a94ae46f5a22b1eb35"
TARGET_URL = "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/compras?compra=06000406000012025"


async def resolver_hcaptcha(page_url, site_key):
    solver = hCaptchaProxyless()
    solver.set_verbose(1)
    solver.set_key(API_KEY)
    solver.set_website_url(page_url)
    solver.set_website_key(site_key)

    print(f"Enviando hCaptcha para Anti-Captcha. SiteKey: {site_key}")
    token = await asyncio.to_thread(solver.solve_and_return_solution)

    if token != 0:
        print("hCaptcha resolvido com sucesso!")
        return token
    else:
        print(f"Erro no Anti-Captcha: {solver.error_code}")
        return None


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            )
        )

        page = await context.new_page()

        # Remove flag de robô (navigator.webdriver)
        await page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        print("Acessando Comprasnet...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded")

        try:
            print("Aguardando carregamento do desafio hCaptcha...")
            captcha_element = await page.wait_for_selector(
                "div.h-captcha", timeout=20000
            )
            site_key = await captcha_element.get_attribute("data-sitekey")

            if not site_key:
                site_key = "b8bbded1-9d04-4ace-9952-b67cde081a7b"
                print(f"SiteKey nao encontrada, usando fallback: {site_key}")

            token = await resolver_hcaptcha(TARGET_URL, site_key)

            if token:
                print("Injetando token de validacao no formulario...")
                # hCaptcha usa elementos <textarea> — deve-se usar .value, nao .innerHTML
                await page.evaluate(f"""
                    (function() {{
                        var hResp = document.querySelector('[name="h-captcha-response"]');
                        var gResp = document.querySelector('[name="g-recaptcha-response"]');
                        if (hResp) hResp.value = '{token}';
                        if (gResp) gResp.value = '{token}';
                    }})();
                """)

                print("Submetendo consulta no Comprasnet...")
                # Tenta o seletor generico primeiro, depois fallback por texto
                submit_btn = page.locator("button[type='submit']").first
                if await submit_btn.count() == 0:
                    submit_btn = page.get_by_role("button", name="Consultar")

                await submit_btn.click()

                await page.wait_for_load_state("networkidle", timeout=30000)
                print("Pagina de dados carregada com sucesso!")

                await asyncio.sleep(10)

        except Exception as e:
            print(f"Erro no fluxo: {e}")
            # Salva screenshot para facilitar debug no VS Code
            await page.screenshot(path="erro_debug.png")
            print("Screenshot salvo em erro_debug.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(run())
