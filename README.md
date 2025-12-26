Automação de Solicitação Operacional

Automação desenvolvida para transformar solicitações enviadas via Google Forms em tarefas estruturadas no ClickUp, com registro em planilha e notificação automática por e-mail, utilizando n8n self-hosted e Google Apps Script.

O objetivo é centralizar solicitações operacionais, padronizar informações e reduzir atividades manuais em ambientes corporativos.

🧩 Tecnologias utilizadas

Google Forms

Google Sheets

Google Apps Script

n8n (Self-hosted)

ClickUp API REST

Gmail (envio de e-mails HTML)

🔄 Fluxo da automação

Usuário envia a solicitação via Google Forms

Google Apps Script captura o evento onFormSubmit

Os dados são enviados via Webhook para o n8n

O n8n cria automaticamente uma tarefa no ClickUp via API

Os campos da tarefa são padronizados com Markdown e emojis

A solicitação é registrada no Google Sheets

Um e-mail de notificação HTML é enviado com os dados da solicitação

📝 Estrutura da tarefa no ClickUp

👤 Solicitante

📝 Descrição detalhada

⚠️ Prioridade, destacada visualmente com emojis

🎯 Diferenciais

Integração real entre múltiplas plataformas

Uso de Webhooks em ambiente self-hosted

Criação automática de tarefas via ClickUp API

Registro histórico das solicitações

Notificação por e-mail com layout profissional

Padronização visual das informações

Projeto pronto para uso em ambiente corporativo

🔐 Segurança

Tokens, URLs reais e IDs sensíveis foram removidos

Uso de placeholders para publicação em repositório público

Nenhuma credencial sensível versionada

📌 Possíveis evoluções

SLA automático por prioridade

Notificações adicionais (WhatsApp / Telegram)

Dashboard de acompanhamento das solicitações

Atribuição automática de responsáveis

💡 Observação
Projeto desenvolvido com foco em boas práticas de automação, clareza operacional e aplicabilidade real, ideal para demonstração em portfólio profissional.

