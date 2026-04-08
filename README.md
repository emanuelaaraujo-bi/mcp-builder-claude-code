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

## Configuracao Global (usar em qualquer projeto)

Por padrao, o `.mcp.json` funciona apenas quando voce abre o Claude Code dentro da pasta do projeto. Para que o MCP Builder fique disponivel **em qualquer diretorio**, basta rodar **um unico comando** no terminal.

> **Antes de comecar:** Voce precisa saber o caminho completo da pasta onde clonou o projeto. Para descobrir, abra o terminal na pasta do projeto e rode:
> - **Linux/Mac:** `pwd`
> - **Windows:** `cd`
>
> Anote o resultado. Exemplo: `/home/joao/mcp-builder-claude-code` ou `C:\Users\joao\mcp-builder-claude-code`

---

### Linux / Mac

Abra o terminal e cole o comando abaixo, **substituindo o caminho** pelo resultado do `pwd`:

```bash
claude mcp add mcp-builder --scope user -e GOOGLE_CLIENT_ID="${GOOGLE_CLIENT_ID}" -e GOOGLE_CLIENT_SECRET="${GOOGLE_CLIENT_SECRET}" -e MCP_BUILDER_URL="${MCP_BUILDER_URL}" -- python /CAMINHO/COMPLETO/PARA/mcp-builder-claude-code/mcp-auth-proxy.py
```

**Exemplo real** (se o projeto esta em `/home/joao/mcp-builder-claude-code`):

```bash
claude mcp add mcp-builder --scope user -e GOOGLE_CLIENT_ID="${GOOGLE_CLIENT_ID}" -e GOOGLE_CLIENT_SECRET="${GOOGLE_CLIENT_SECRET}" -e MCP_BUILDER_URL="${MCP_BUILDER_URL}" -- python /home/joao/mcp-builder-claude-code/mcp-auth-proxy.py
```

---

### Windows

Abra o **PowerShell** e cole o comando abaixo, **substituindo o caminho** pelo local onde voce clonou o projeto:

```powershell
claude mcp add mcp-builder --scope user -e GOOGLE_CLIENT_ID="$env:GOOGLE_CLIENT_ID" -e GOOGLE_CLIENT_SECRET="$env:GOOGLE_CLIENT_SECRET" -e MCP_BUILDER_URL="$env:MCP_BUILDER_URL" -- python C:\CAMINHO\COMPLETO\PARA\mcp-builder-claude-code\mcp-auth-proxy.py
```

**Exemplo real** (se o projeto esta em `C:\Users\joao\mcp-builder-claude-code`):

```powershell
claude mcp add mcp-builder --scope user -e GOOGLE_CLIENT_ID="$env:GOOGLE_CLIENT_ID" -e GOOGLE_CLIENT_SECRET="$env:GOOGLE_CLIENT_SECRET" -e MCP_BUILDER_URL="$env:MCP_BUILDER_URL" -- python C:\Users\joao\mcp-builder-claude-code\mcp-auth-proxy.py
```

---

### Verificando se funcionou

1. Abra o Claude Code em **qualquer pasta**:
   ```bash
   claude
   ```
2. Dentro do Claude Code, digite:
   ```
   /mcp
   ```
3. O servidor `mcp-builder` deve aparecer na lista como **connected**.

### Removendo a configuracao global

Se precisar remover:

```bash
claude mcp remove mcp-builder --scope user
```

> **Dica:** Se voce mudar o projeto de pasta, rode o comando `claude mcp add` novamente com o novo caminho.

## Renovacao de token

O token e salvo em `~/.mcp-builder/` e renovado automaticamente. Se expirar ou houver problemas, execute o passo 4 novamente.
