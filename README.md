# Automação de Solicitação Operacional

Automação desenvolvida para transformar solicitações enviadas via Google Forms em tarefas no ClickUp, utilizando n8n self-hosted e Google Apps Script.

## 🧩 Tecnologias utilizadas
- Google Forms
- Google Sheets
- Google Apps Script
- n8n (Self-hosted)
- ClickUp API REST

## 🔄 Fluxo da automação
1. Usuário envia solicitação via Google Forms
2. Google Apps Script captura o evento `onFormSubmit`
3. Dados são enviados via webhook para o n8n
4. n8n cria tarefa no ClickUp via API
5. Campos são padronizados com Markdown e emojis
6. Registro é salvo no Google Sheets

## 📝 Estrutura da tarefa no ClickUp
- 👤 Solicitante
- 📝 Descrição
- ⚠️ Prioridade (visual com emojis)

## 🎯 Diferenciais
- Integração real entre múltiplas plataformas
- Uso de Webhooks
- Tratamento de erros e permissões da API
- Padronização visual profissional
- Projeto pronto para ambiente corporativo

## 🔐 Segurança
Tokens, URLs reais e IDs sensíveis foram removidos e substituídos por placeholders.

## 📌 Possíveis evoluções
- SLA automático por prioridade
- Notificações (Email / WhatsApp / Telegram)
- Dashboard de solicitações

