## Capivarinha CLI

### 🎯 O que é

`capi-cli` é uma ferramenta de linha de comando em **Python puro** para interagir com **Variable Groups** do Azure DevOps:

* **pesquisar**: encontra variáveis cujo **valor** contém um termo informado.
* **baixar**: exporta todas as variáveis de um **Variable Group (lib)** para um arquivo `.env`.

### ✅ Requisitos

* **Python 3.8+**
* **Azure CLI (az)** instalada
* Você precisa estar autenticado no Azure: `az login`

> Dica: se usa múltiplas orgs/projetos, valide permissões com `az account show` e `az devops configure --defaults organization=<URL>` se quiser.

### 🧩 Instalação (opcional)

Você pode simplesmente usar o arquivo `capivarinha_cli.py` sem instalar nada, mas se preferir instalar globalmente:

```bash
# macOS/Linux
chmod +x capi-cli.py
sudo cp capi-cli.py /usr/local/bin/capi-cli
```

No Windows (PowerShell como Admin):

```powershell
Copy-Item .\capi-cli.py "C:\\Windows\\System32\\capi-cli.py"
# Agora você pode chamar com: python3 C:\\Windows\\System32\\capi-cli.py ...
```

> Alternativamente, adicione a pasta do script ao `PATH` e chame `python3 capi-cli.py`.

### ▶️ Executar **sem** instalação

Basta rodar com Python diretamente (macOS/Windows/Linux):

```bash
python3 capi-cli.py pesquisar --termo=lorem-ipsum \
  --projeto=TEST --ambiente=DEV \
  --salvar=resultado.txt --out \
  --organizacao=https://dev.azure.com/minha-org
```

Ou baixar .env de uma *lib* específica:

```bash
python3 capi-cli.py baixar \
  --projeto=TEST \
  --ambiente=DEV \
  --salvar=.env --out \
  --organizacao=https://dev.azure.com/minha-org \
  --lib=MEU-APP.DEV
```

### 🔧 Comandos e parâmetros

#### `pesquisar`

* `--organizacao` **(obrigatório)**: URL da organização. Ex.: `https://dev.azure.com/minha-org`
* `--termo` **(obrigatório)**: termo a ser buscado **no valor** das variáveis
* `--projeto` *(opcional)*: filtro de projeto (substring)
* `--ambiente` *(opcional)*: `DEV | QAS | UAT | HTX | PRD` (filtra pelo nome do grupo)
* `--salvar` *(opcional)*: caminho para salvar resultado em texto
* `--out` *(opcional)*: também exibe no terminal

**Exemplo:**

```bash
capi-cli pesquisar --termo=https://my-legacy-api --projeto=TEST \
  --ambiente=QAS --salvar=resultado.txt --out \
  --organizacao=https://dev.azure.com/minha-org
```

#### `baixar`

* `--organizacao` **(obrigatório)**
* `--projeto` **(obrigatório)**: nome ou substring do projeto onde está a lib
* `--lib` **(obrigatório)**: nome do Variable Group (lib) — casa exato primeiro, senão substring
* `--ambiente` *(opcional)*: restringe pelo ambiente no nome do grupo
* `--salvar` *(opcional)*: caminho do arquivo `.env`
* `--out` *(opcional)*: também exibe o `.env` no terminal

**Exemplo:**

```bash
capi-cli baixar --projeto=TEST --ambiente=QAS \
  --salvar=.env --out \
  --organizacao=https://dev.azure.com/minha-org \
  --lib=Meu-App.QAS
```

### 📦 Saída

* **pesquisar**: lista `projeto`, `grupo`, `chave`, `valor`, `criado_por`, `modificado_por`.
* **baixar**: gera linhas no formato `KEY=VALUE`.

  * Observação: valores de **segredos** podem não ser retornados pela Azure CLI com `list` e serão marcados como `***SECRET***`.

### 🖥️ UX no terminal

O script exibe **spinners discretos** para indicar progresso (`Listando projetos...`, `Analisando grupos...`) e limpa a linha ao final para não poluir a saída.

### ⚠️ Limitações conhecidas

* A busca é **case-sensitive** (igual ao script original). Ajuste em `_match` se quiser case-insensitive.
* Para segredos, a API de listagem não retorna o valor — exportaremos `***SECRET***` como marcador.

### 🛠️ Solução de problemas

* **`az: command not found`**: instale a Azure CLI.
* **Permissão negada**: certifique-se de estar logado (`az login`) e com acesso aos projetos/variable groups.
* **Sem resultados**: verifique filtros de `--projeto`, `--ambiente` e o `--termo`.

### 📚 Boas práticas aplicadas

* **Clean Code & SOLID**: fachada `AzureDevOps`, funções puras para serialização, separação clara de camadas (I/O, domínio, apresentação).
* **Docstrings** detalhadas e *type hints* para facilitar manutenção.
* **Sem dependências externas**: apenas `subprocess`, `json`, `argparse` e utilitários da stdlib.

### 💡 Sugestões futuras

* Flag `--ignore-case` para busca case-insensitive.
* Suporte a múltiplas libs no `baixar` (ex.: `--lib LIB1 --lib LIB2`).
* Comando `listar` para inspecionar groups/projetos rapidamente.
* Exportar para JSON/YAML além de `.env`.

---

## Exemplos rápidos

```bash
# 1) Pesquisar termo em todos os projetos e ambientes
capi-cli pesquisar --organizacao=https://dev.azure.com/minha-org --termo=mongodb://test --out

# 2) Pesquisar limitado ao projeto TEST e ambiente DEV e salvar
capi-cli pesquisar --organizacao=https://dev.azure.com/minha-org \
  --termo=lorem --projeto=TEST --ambiente=DEV --salvar=resultado.txt

# 3) Baixar .env de uma lib específica
capi-cli baixar --organizacao=https://dev.azure.com/minha-org \
  --projeto=TEST --lib=Minha-Api.QAS --salvar=.env --out
```

## Instalação Rápida

---

## Comando simples para instalar direto do GitHub

### Linux / macOS

```bash
git clone https://github.com/4lessandrodev/capivarinha-cli.git && \
cd capivarinha-cli && \
chmod +x capi-cli.py && \
sudo cp capi-cli.py /usr/local/bin/capi-cli && \
cd .. && \
rm -rf capivarinha-cli
```

---

### Windows (PowerShell)

```powershell
git clone https://github.com/4lessandrodev/capivarinha-cli.git
Set-Location capivarinha-cli
Copy-Item .\capi-cli.py "C:\Program Files\capi-cli\capi-cli.py"
# Criar o bat para chamar facilmente
'@echo off
python "%~dp0\capi-cli.py" %*
' | Out-File "C:\Program Files\capi-cli\capi-cli.bat" -Encoding ASCII
```

Depois certifique de que `C:\Program Files\capi-cli` esteja no PATH.
