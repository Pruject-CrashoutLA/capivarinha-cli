# 🐾 Capivarinha CLI (`capi-cli`)

Uma CLI em **Python puro** para interagir com **Variable Groups** do Azure DevOps.

---

## ✨ Funcionalidades

* 🔍 **Pesquisar**: encontra variáveis cujo **valor** contém um termo informado.
* 📥 **Baixar**: exporta todas as variáveis de um **Variable Group (lib)** para um arquivo `.env`.

---

## ✅ Pré-requisitos

* **Python 3.8+**
* **Azure CLI (`az`)** instalada
* Autenticação ativa:

  ```bash
  az login
  ```
* Se necessário, instale a extensão do DevOps:

  ```bash
  az extension add --name azure-devops
  ```

> 💡 **Dica**: se você usa múltiplas organizações/projetos, configure os defaults:
>
> ```bash
> az account show
> az devops configure --defaults organization=https://dev.azure.com/minha-org
> ```

---

## ⚙️ Instalação (opcional)

Você pode rodar direto o arquivo `capi-cli.py`, mas se preferir instalar globalmente:

### Linux / macOS

```bash
chmod +x capi-cli.py
sudo cp capi-cli.py /usr/local/bin/capi-cli
```

### Windows (PowerShell como Admin)

```powershell
Copy-Item .\capi-cli.py "C:\Windows\System32\capi-cli.py"
# Agora você pode chamar com:
python C:\Windows\System32\capi-cli.py ...
```

Ou adicione a pasta do script ao `PATH`.

---

## ▶️ Como usar sem instalação

Execute diretamente com Python:

```bash
python3 capi-cli.py pesquisar \
  --termo=lorem-ipsum \
  --projeto=TEST --ambiente=DEV \
  --salvar=resultado.txt --out \
  --organizacao=https://dev.azure.com/minha-org
```

Exportar `.env` de uma lib específica:

```bash
python3 capi-cli.py baixar \
  --projeto=TEST --ambiente=DEV \
  --salvar=.env --out \
  --organizacao=https://dev.azure.com/minha-org \
  --lib=MEU-APP.DEV
```

---

## 🔧 Comandos e parâmetros

### 🔍 `pesquisar`

| Parâmetro       | Obrigatório | Descrição                                                   |
| --------------- | ----------- | ----------------------------------------------------------- |
| `--organizacao` | ✅           | URL da organização (ex.: `https://dev.azure.com/minha-org`) |
| `--termo`       | ✅           | Termo a ser buscado nos valores                             |
| `--projeto`     | ❌           | Filtro por nome/substring de projeto                        |
| `--ambiente`    | ❌           | Filtra pelo nome do grupo (`DEV`, `QAS`, etc.)              |
| `--ignore-case` | ❌           | Busca sem diferenciar maiúsculas/minúsculas                 |
| `--salvar`      | ❌           | Salvar saída em arquivo texto                               |
| `--out`         | ❌           | Exibir resultados no terminal                               |

📌 Exemplo:

```bash
capi-cli pesquisar \
  --organizacao=https://dev.azure.com/minha-org \
  --termo=https://my-legacy-api \
  --projeto=TEST --ambiente=QAS \
  --salvar=resultado.txt --out
```

---

### 📥 `baixar`

| Parâmetro       | Obrigatório | Descrição                                         |
| --------------- | ----------- | ------------------------------------------------- |
| `--organizacao` | ✅           | URL da organização                                |
| `--projeto`     | ✅           | Nome/substring do projeto                         |
| `--lib`         | ✅           | Nome do Variable Group (match exato ou substring) |
| `--ambiente`    | ❌           | Filtra pelo nome do grupo contendo o ambiente     |
| `--salvar`      | ❌           | Caminho do arquivo `.env`                         |
| `--out`         | ❌           | Exibir `.env` no terminal                         |

📌 Exemplo:

```bash
capi-cli baixar \
  --organizacao=https://dev.azure.com/minha-org \
  --projeto=TEST \
  --lib=Meu-App.QAS \
  --ambiente=QAS \
  --salvar=.env --out
```

---

## 📦 Saída

* **pesquisar** → lista:

  ```
  projeto | grupo | chave | valor | criado_por | modificado_por
  ```

* **baixar** → gera `.env` no formato:

  ```
  KEY=VALUE
  ```

> 🔒 **Segredos** não são retornados pela Azure CLI — aparecem como `***SECRET***`.

---

## 🖥️ Experiência no terminal

* Exibe **spinners discretos** (`Listando projetos...`, `Analisando grupos...`)
* Limpa a linha ao final → saída limpa e organizada

---

## ⚠️ Limitações atuais

* Busca é **case-sensitive** por padrão (use `--ignore-case` se quiser sem diferenciação).
* Segredos não podem ser exportados (limitado pela API da Azure CLI).

---

## 🛠️ Solução de problemas

* **`az: command not found`** → instale a Azure CLI.
* **Permissão negada** → valide login com `az login` e permissões nos projetos.
* **Sem resultados** → revise filtros (`--projeto`, `--ambiente`, `--termo`).

---

## 📚 Boas práticas aplicadas

* Arquitetura limpa (Clean Code & SOLID)
* Fachada `AzureDevOps`, funções puras e separação clara de responsabilidades
* **Docstrings + type hints** para fácil manutenção
* **Zero dependências externas** além da stdlib do Python

---

## 🚀 Roadmap / Sugestões futuras

* Exportar também para JSON ou YAML
* Suporte a múltiplas libs no comando `baixar` (`--lib LIB1 --lib LIB2`)
* Novo comando `listar` para exibir rapidamente projetos e grupos

---

## ⚡ Instalação rápida via GitHub

### Linux / macOS

```bash
git clone https://github.com/4lessandrodev/capivarinha-cli.git && \
cd capivarinha-cli && \
chmod +x capi-cli.py && \
sudo cp capi-cli.py /usr/local/bin/capi-cli && \
cd .. && rm -rf capivarinha-cli
```

### Windows (PowerShell)

```powershell
git clone https://github.com/4lessandrodev/capivarinha-cli.git
Set-Location capivarinha-cli
Copy-Item .\capi-cli.py "C:\Program Files\capi-cli\capi-cli.py"
'@echo off
python "%~dp0\capi-cli.py" %*
' | Out-File "C:\Program Files\capi-cli\capi-cli.bat" -Encoding ASCII
```

> Depois, adicione `C:\Program Files\capi-cli` ao `PATH` se necessário.
