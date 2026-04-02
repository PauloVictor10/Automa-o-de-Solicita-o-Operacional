#!/usr/bin/env python3
"""
Capturador de Token de Captcha - ComprasNet
===========================================
Abre o browser ComprasNet, intercepta o token P1_eyJ... das requisições
e salva em 'token.txt' para usar no bot principal.

Uso:
  python3 capturar_token.py

Depois:
  python3 comprasnet_bot.py --token "$(cat token.txt)"
  # ou
  CAPTCHA_TOKEN=$(cat token.txt) python3 comprasnet_bot.py
"""

import asyncio
import sys
import time


PORTAL_URL = "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-fase-externa/"
API_PATH = "/comprasnet-fase-externa/public/v1/compras"

STEALTH_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US'] });
Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {},
};
Object.defineProperty(navigator, 'permissions', {
    get: () => ({
        query: function(x) { return Promise.resolve({ state: 'granted' }); }
    })
});
const origGetter = WebGLRenderingContext.prototype.__lookupGetter__('vendor');
Object.defineProperty(WebGLRenderingContext.prototype, 'vendor', {
    get: function() { return 'Google Inc.'; }
});
"""


async def capturar_token():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("ERRO: Playwright não instalado.")
        print("Instale com: pip install playwright && playwright install chromium")
        sys.exit(1)

    print("=" * 60)
    print(" CAPTURADOR DE TOKEN - ComprasNet")
    print("=" * 60)
    print(f"\nAbrindo: {PORTAL_URL}")
    print("\nINSTRUÇÕES:")
    print("1. O browser abrirá automaticamente")
    print("2. Navegue até a seção de Compras/Licitações")
    print("3. O token será capturado automaticamente das requisições")
    print("4. Aguarde a confirmação de captura")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-infobars",
                "--window-size=1366,768",
            ],
        )

        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
            extra_http_headers={
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
            },
            locale="pt-BR",
        )

        await context.add_init_script(STEALTH_SCRIPT)

        page = await context.new_page()

        tokens_encontrados = []
        ultimo_token = {"valor": None, "ts": 0}

        async def on_request(request):
            url = request.url
            if API_PATH in url and "captcha=" in url:
                try:
                    parte = url.split("captcha=")[1]
                    token = parte.split("&")[0]
                    if (token
                            and len(token) > 100
                            and token.startswith("P1_")
                            and token != ultimo_token["valor"]):
                        ultimo_token["valor"] = token
                        ultimo_token["ts"] = time.time()
                        tokens_encontrados.append(token)
                        print(f"\n TOKEN CAPTURADO ({len(tokens_encontrados)}): {token[:70]}...")
                except Exception:
                    pass

        page.on("request", on_request)

        print(f"Navegando para {PORTAL_URL}...")
        try:
            await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=60_000)
        except Exception as e:
            print(f"Aviso no carregamento: {e}")

        # Tenta clicar em links de compras para acionar a API
        await asyncio.sleep(3)
        for seletor in [
            "a[href*='compras']",
            "a[href*='licitacoes']",
            "button[class*='compra']",
            "nav a",
        ]:
            try:
                elementos = await page.query_selector_all(seletor)
                for el in elementos[:2]:
                    await el.click()
                    await asyncio.sleep(1)
                    if tokens_encontrados:
                        break
                if tokens_encontrados:
                    break
            except Exception:
                pass

        # Aguarda até 90 segundos pelo token
        print("\nAguardando token (máx. 90s)... Navegue no browser se necessário.")
        for i in range(90):
            await asyncio.sleep(1)
            if tokens_encontrados:
                # Aguarda mais 2s para capturar tokens adicionais
                await asyncio.sleep(2)
                break
            if (i + 1) % 10 == 0:
                print(f"  ...{i + 1}s aguardados")

        await browser.close()

        if not tokens_encontrados:
            print("\n ERRO: Nenhum token capturado.")
            print("Tente navegar manualmente até a seção de compras.")
            sys.exit(1)

        # Usa o token mais recente
        token_final = tokens_encontrados[-1]

        # Salva em arquivo
        with open("token.txt", "w") as f:
            f.write(token_final)

        print(f"\n Token salvo em: token.txt")
        print(f" Total capturado: {len(tokens_encontrados)} tokens")
        print(f" Token atual: {token_final[:80]}...")
        print()
        print("PRÓXIMO PASSO:")
        print('  python3 comprasnet_bot.py --token "$(cat token.txt)"')
        print()

        return token_final


if __name__ == "__main__":
    asyncio.run(capturar_token())
