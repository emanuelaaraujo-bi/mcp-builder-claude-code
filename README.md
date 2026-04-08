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

Por padrao, o `.mcp.json` funciona apenas quando voce abre o Claude Code dentro da pasta do projeto. Para que o MCP Builder fique disponivel **em qualquer diretorio**, siga os passos abaixo:

### Opcao 1: Via comando do Claude Code (recomendado)

Dentro do Claude Code, digite:

```
/mcp
```

Selecione **"Add new MCP server"**, depois **"command (stdio)"**, e preencha:

- **Name:** `mcp-builder`
- **Command:** `python`
- **Args:** caminho absoluto para o script, por exemplo:
  - Linux/Mac: `/home/seu-usuario/mcp-builder-claude-code/mcp-auth-proxy.py`
  - Windows: `C:\Users\seu-usuario\mcp-builder-claude-code\mcp-auth-proxy.py`

Escolha o escopo **"User"** para que fique disponivel globalmente.

### Opcao 2: Editando o arquivo manualmente

O Claude Code armazena configuracoes globais de MCP no arquivo:

| SO | Caminho |
|---|---|
| **Linux/Mac** | `~/.claude/.mcp.json` |
| **Windows** | `C:\Users\<seu-usuario>\.claude\.mcp.json` |

**Passo 1:** Crie (ou edite) o arquivo `.mcp.json` na pasta `~/.claude/`:

**Linux/Mac:**

```bash
mkdir -p ~/.claude
nano ~/.claude/.mcp.json
```

**Windows (PowerShell):**

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude"
notepad "$env:USERPROFILE\.claude\.mcp.json"
```

**Passo 2:** Cole o conteudo abaixo, ajustando o caminho absoluto do script:

**Linux/Mac:**

```json
{
  "mcpServers": {
    "mcp-builder": {
      "type": "command",
      "command": "python",
      "args": ["/caminho/completo/para/mcp-builder-claude-code/mcp-auth-proxy.py"],
      "env": {
        "GOOGLE_CLIENT_ID": "${GOOGLE_CLIENT_ID}",
        "GOOGLE_CLIENT_SECRET": "${GOOGLE_CLIENT_SECRET}",
        "MCP_BUILDER_URL": "${MCP_BUILDER_URL}"
      }
    }
  }
}
```

**Windows:**

```json
{
  "mcpServers": {
    "mcp-builder": {
      "type": "command",
      "command": "python",
      "args": ["C:\\Users\\seu-usuario\\mcp-builder-claude-code\\mcp-auth-proxy.py"],
      "env": {
        "GOOGLE_CLIENT_ID": "${GOOGLE_CLIENT_ID}",
        "GOOGLE_CLIENT_SECRET": "${GOOGLE_CLIENT_SECRET}",
        "MCP_BUILDER_URL": "${MCP_BUILDER_URL}"
      }
    }
  }
}
```

**Passo 3:** Reinicie o Claude Code e verifique com `/mcp` — o servidor `mcp-builder` deve aparecer independentemente do diretorio em que voce estiver.

> **Importante:** O caminho para `mcp-auth-proxy.py` deve ser **absoluto** (completo), pois o Claude Code pode ser aberto de qualquer diretorio. Caminhos relativos so funcionam quando voce esta dentro da pasta do projeto.

> **Dica:** Se voce ja tem um `.mcp.json` global com outros servidores, basta adicionar a entrada `"mcp-builder"` dentro do objeto `"mcpServers"` existente.

## Renovacao de token

O token e salvo em `~/.mcp-builder/` e renovado automaticamente. Se expirar ou houver problemas, execute o passo 4 novamente.
