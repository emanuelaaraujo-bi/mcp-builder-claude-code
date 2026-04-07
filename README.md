# MCP Builder - Claude Code

Configuracao do MCP (Model Context Protocol) para integracao do Claude Code com o MCP Builder.

## Pre-requisitos

- Python 3.10+
- Claude Code instalado
- Acesso autorizado ao MCP Builder (peca ao admin para liberar seu email)
- Credenciais OAuth fornecidas pelo administrador do projeto

## Setup

### 1. Clone o repositorio

```bash
git clone https://github.com/emanuelaaraujo-bi/mcp-builder-claude-code.git
cd mcp-builder-claude-code
```

### 2. Instale as dependencias Python

```bash
pip install httpx google-auth-oauthlib
```

### 3. Configure as variaveis de ambiente

Solicite as credenciais ao administrador do projeto e configure as variaveis de ambiente:

**Linux/Mac (adicione ao `~/.bashrc` ou `~/.zshrc`):**

```bash
export GOOGLE_CLIENT_ID="<seu-client-id>"
export GOOGLE_CLIENT_SECRET="<seu-client-secret>"
export MCP_BUILDER_URL="<url-do-mcp-builder>"
```

**Windows (CMD):**

```cmd
setx GOOGLE_CLIENT_ID "<seu-client-id>"
setx GOOGLE_CLIENT_SECRET "<seu-client-secret>"
setx MCP_BUILDER_URL "<url-do-mcp-builder>"
```

**Windows (PowerShell):**

```powershell
[Environment]::SetEnvironmentVariable("GOOGLE_CLIENT_ID", "<seu-client-id>", "User")
[Environment]::SetEnvironmentVariable("GOOGLE_CLIENT_SECRET", "<seu-client-secret>", "User")
[Environment]::SetEnvironmentVariable("MCP_BUILDER_URL", "<url-do-mcp-builder>", "User")
```

> Depois de configurar, reinicie o terminal para que as variaveis sejam carregadas.

### 4. Faca o login inicial

Execute o comando abaixo. Um browser sera aberto para autenticacao com sua conta Google:

```bash
python mcp-auth-proxy.py --login-only
```

Se o login for bem-sucedido, voce vera: `Authentication successful!`

> **Nota:** Se receber o erro `User '...' is not authorized`, peca ao administrador para liberar seu email no servidor MCP Builder.

### 5. Abra o Claude Code

```bash
cd mcp-builder-claude-code
claude
```

O Claude Code detecta automaticamente o `.mcp.json` e conecta ao servidor MCP Builder. Verifique digitando `/mcp` dentro do Claude Code.

## Estrutura do projeto

```
.mcp.json              # Configuracao do servidor MCP para o Claude Code
mcp-auth-proxy.py      # Proxy de autenticacao Google OAuth -> MCP
README.md              # Este arquivo
```

## Renovacao de token

O token e salvo em `~/.mcp-builder/` e renovado automaticamente. Se expirar ou houver problemas, execute o passo 4 novamente.
