# Setup — ActiveCampaign → Google Sheets → Looker Studio

## 1. Instalar dependências

```bash
pip install -r requirements.txt
```

## 2. Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha:

```bash
cp .env.example .env
```

Edite o `.env`:
```
AC_API_URL=https://bling25662.api-us1.com
AC_API_KEY=SUA_API_KEY_AQUI
GOOGLE_SHEET_ID=ID_DA_SUA_PLANILHA
GOOGLE_CREDENTIALS_FILE=credentials.json
```

## 3. Configurar Google Sheets (Service Account)

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto (ou use um existente)
3. Ative as APIs: **Google Sheets API** e **Google Drive API**
4. Vá em **IAM & Admin → Service Accounts → Create Service Account**
5. Baixe o JSON de credenciais e salve como `credentials.json` na raiz do projeto
6. Crie uma planilha no Google Sheets e **compartilhe com o e-mail da Service Account** (com permissão de Editor)
7. Copie o ID da planilha da URL: `https://docs.google.com/spreadsheets/d/**SEU_ID_AQUI**/edit`

## 4. Executar extração

```bash
python activecampaign_extractor.py
```

O script cria/atualiza duas abas na planilha:
- **Campanhas** — dados de todas as campanhas
- **Automacoes** — dados de todas as automações

## 5. Conectar no Looker Studio

1. Acesse [Looker Studio](https://lookerstudio.google.com/)
2. Clique em **Criar → Relatório**
3. Selecione **Google Sheets** como fonte de dados
4. Escolha sua planilha e a aba **Campanhas** ou **Automacoes**
5. Repita para adicionar as duas abas como fontes separadas

## Métricas disponíveis

### Campanhas
| Campo | Descrição |
|-------|-----------|
| total_enviados | Total de e-mails enviados |
| total_abertos | Total de aberturas |
| total_cliques | Cliques únicos em links |
| taxa_abertura | Taxa de abertura (%) |
| taxa_clique | Taxa de clique (%) |
| total_bounces | Hard bounces |
| total_descadastros | Descadastros |

### Automações
| Campo | Descrição |
|-------|-----------|
| total_contatos | Total de contatos que entraram |
| contatos_ativos | Contatos atualmente na automação |
| contatos_concluidos | Contatos que concluíram |
| ativa | Se a automação está ativa |
