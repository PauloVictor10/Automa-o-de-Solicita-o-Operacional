# ComprasNet Bot — Raspagem de Licitações

Bot para coleta automática de dados de compras homologadas no portal **ComprasNet (SERPRO/Gov.br)** e exportação para planilha Excel.

---

## O problema do iCaptcha

O site usa o **iCaptcha SERPRO** (`P1_eyJ...`), um JWT assinado com HS256 que:
- É gerado pelo JavaScript do portal a cada sessão
- Tem expiração curta (~15–30 min)
- **Não pode ser forjado** (chave secreta fica no servidor)

Por isso, a estratégia é **capturar o token do browser** e usá-lo nas chamadas à API.

---

## Instalação

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## Uso — 3 modos disponíveis

### Modo 1 — Automático (Playwright captura o token)

```bash
python3 comprasnet_bot.py --ano 2025
```

O browser abrirá automaticamente. Se o token não for capturado em 45s,
navegue manualmente até a seção de compras.

---

### Modo 2 — Token manual (mais confiável)

**Passo 1:** Capture o token separadamente:
```bash
python3 capturar_token.py
# Browser abre → navegue em Compras → token salvo em token.txt
```

**Passo 2:** Execute o bot com o token:
```bash
python3 comprasnet_bot.py --token "$(cat token.txt)"
# ou
CAPTCHA_TOKEN=$(cat token.txt) python3 comprasnet_bot.py
```

---

### Modo 3 — Token copiado do browser manualmente

1. Abra o Chrome, acesse o portal
2. Abra DevTools (F12) → aba **Network**
3. Procure qualquer requisição com `captcha=P1_...` na URL
4. Copie o valor do parâmetro `captcha`

```bash
python3 comprasnet_bot.py --manual
# Cola o token quando solicitado
```

---

## Opções

```
--token / -t    Token P1_eyJ... diretamente
--ano   / -a    Ano das compras (padrão: 2025)
--paginas / -p  Máximo de páginas (50 compras/pág, padrão: 10 = 500 compras)
--manual / -m   Forçar input manual do token
```

**Exemplos:**
```bash
# Apenas 1 página (50 compras, mais rápido para teste)
python3 comprasnet_bot.py --token "P1_eyJ..." --paginas 1

# Todas as páginas de 2024
python3 comprasnet_bot.py --token "P1_eyJ..." --ano 2024 --paginas 999
```

---

## Saída

Gera o arquivo: `comprasnet_2025_YYYYMMDD_HHMMSS.xlsx`

| Aba | Conteúdo |
|-----|----------|
| **Resumo** | Totais e informações da coleta |
| **Compras** | Lista de licitações (código, objeto, órgão, valor, datas) |
| **Itens** | Itens/lotes de cada compra |
| **Propostas** | Propostas dos fornecedores por item |

---

## Endpoints da API usados

| Operação | Endpoint |
|----------|----------|
| Listar compras | `GET /compras?captcha=...&filtro=...` |
| Detalhe compra | `GET /compras/{codigoCompra}?captcha=...` |
| Itens | `GET /compras/{id}/itens?captcha=...` |
| Propostas | `GET /compras/{id}/itens/{n}/propostas?captcha=...` |

---

## Dicas

- **Token expira rapidamente** — use logo após capturar
- Se receber erro 401/403, o token expirou — capture um novo
- Para grandes volumes, use `--paginas 1` primeiro para testar
- O bot aguarda ~0.4s entre requisições para evitar bloqueio
