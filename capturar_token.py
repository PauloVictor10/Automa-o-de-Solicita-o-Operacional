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
// Remove indicadores de webdriver
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
delete navigator.__proto__.webdriver;

// Plugins realistas
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const arr = [
            { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
            { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
            { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' },
        ];
        arr.__proto__ = PluginArray.prototype;
        return arr;
    }
});

// Idiomas
Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US', 'en'] });

// Plataforma
Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });

// Hardware concurrency (núcleos reais)
Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });

// Memória de dispositivo
Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });

// Chrome runtime
window.chrome = {
    app: { isInstalled: false, InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' }, RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' } },
    runtime: { OnInstalledReason: { CHROME_UPDATE: 'chrome_update', INSTALL: 'install', SHARED_MODULE_UPDATE: 'shared_module_update', UPDATE: 'update' }, OnRestartRequiredReason: { APP_UPDATE: 'app_update', OS_UPDATE: 'os_update', PERIODIC: 'periodic' }, PlatformArch: { ARM: 'arm', ARM64: 'arm64', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' }, PlatformNaclArch: { ARM: 'arm', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' }, PlatformOs: { ANDROID: 'android', CROS: 'cros', LINUX: 'linux', MAC: 'mac', OPENBSD: 'openbsd', WIN: 'win' }, RequestUpdateCheckStatus: { NO_UPDATE: 'no_update', THROTTLED: 'throttled', UPDATE_AVAILABLE: 'update_available' } },
    loadTimes: function() {},
    csi: function() {},
};

// Permissions API
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);

// WebGL vendor/renderer realistas
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) return 'Intel Inc.';
    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
    return getParameter.call(this, parameter);
};

// Evitar detecção por toString()
const nativeToStringFunctionString = Error.toString.bind(Error);
const oldCall = Function.prototype.call;
function call() { return oldCall.apply(this, arguments); }
Function.prototype.call = call;
const nativeToString = Function.prototype.toString;
Function.prototype.toString = function() {
    if (this === call) return 'function call() { [native code] }';
    return nativeToString.call(this);
};
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

        # ── Navegação em etapas para acionar a geração do captcha ──────────

        # Etapa 1: portal principal (carrega JS do iCaptcha)
        print(f"[1/3] Carregando portal principal...")
        try:
            await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=60_000)
        except Exception as e:
            print(f"  Aviso: {e}")
        await asyncio.sleep(3)

        if not tokens_encontrados:
            # Etapa 2: navegar para a rota de compras dentro do SPA
            rotas_spa = [
                f"{PORTAL_URL}#/compras",
                f"{PORTAL_URL}#/licitacoes",
                f"{PORTAL_URL}compras",
            ]
            for rota in rotas_spa:
                print(f"[2/3] Tentando rota: {rota}")
                try:
                    await page.goto(rota, wait_until="domcontentloaded", timeout=20_000)
                    await asyncio.sleep(3)
                    if tokens_encontrados:
                        break
                except Exception:
                    pass

        if not tokens_encontrados:
            # Etapa 3: clicar nos links da página
            print("[3/3] Procurando links de compras para clicar...")
            for seletor in [
                "a[href*='compras']", "a[href*='licitacoes']",
                "button[class*='compra']", "button[class*='licita']",
                "nav a", "header a", ".menu a",
            ]:
                try:
                    elementos = await page.query_selector_all(seletor)
                    for el in elementos[:3]:
                        try:
                            await el.click()
                            await asyncio.sleep(2)
                            if tokens_encontrados:
                                break
                        except Exception:
                            pass
                    if tokens_encontrados:
                        break
                except Exception:
                    pass

        # Aguarda até 90 segundos; o usuário pode navegar manualmente
        print("\nAguardando token (máx. 90s)...")
        if not tokens_encontrados:
            print("Se o browser travar ou pedir interação, faça isso agora.")
        for i in range(90):
            await asyncio.sleep(1)
            if tokens_encontrados:
                await asyncio.sleep(2)   # captura tokens adicionais
                break
            if (i + 1) % 15 == 0:
                print(f"  ...{i + 1}s aguardados (navegue até Compras se necessário)")

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
