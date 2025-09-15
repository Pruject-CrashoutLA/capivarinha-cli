# 🐾 Capivarinha CLI (`capi-cli`)

Uma CLI em **Python puro** para interagir com **Variable Groups** do Azure DevOps.

---

## ✨ Funcionalidades

* 🔍 **Pesquisar**: encontra variáveis cujo **valor** contém um termo informado.  
* 📥 **Baixar**: exporta todas as variáveis de um **Variable Group (lib)** para um arquivo `.env`.  
* 📂 **Listar**: exibe todas as variáveis de um projeto/grupo, sem filtro por termo.  

---

## ✅ Pré-requisitos

* **Python 3.8+**
* **Azure CLI (`az`)** instalada
* Autenticação ativa:

```bash
az login
````

Se necessário, instale a extensão do DevOps:

```bash
az extension add --name azure-devops
```

---

## ⚙️ Instalação

Você pode rodar direto o arquivo `capi-cli.py`, mas se preferir instalar globalmente:

### Via Makefile (Linux/macOS)

```bash
make instalar
```

### Manual

```bash
chmod +x capi-cli.py
sudo cp capi-cli.py /usr/local/bin/capi-cli
```

### Windows (PowerShell como Admin)

```powershell
Copy-Item .\capi-cli.py "C:\Windows\System32\capi-cli.py"
python C:\Windows\System32\capi-cli.py ...
```

---

## ▶️ Como usar

### Pesquisar

```bash
capi-cli pesquisar \
  --organizacao=https://dev.azure.com/minha-org \
  --termo=https://my-api \
  --projeto=TEST --ambiente=QAS \
  --salvar=resultado.txt --out
```

### Baixar

```bash
capi-cli baixar \
  --organizacao=https://dev.azure.com/minha-org \
  --projeto=TEST \
  --lib=Meu-App.QAS \
  --ambiente=QAS \
  --salvar=.env --out
```

### Listar

```bash
capi-cli listar \
  --organizacao=https://dev.azure.com/minha-org \
  --projeto=COCKPIT --ambiente=DEV \
  --salvar=variaveis.txt --out
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

---

### 📂 `listar`

| Parâmetro       | Obrigatório | Descrição                                     |
| --------------- | ----------- | --------------------------------------------- |
| `--organizacao` | ✅           | URL da organização                            |
| `--projeto`     | ✅           | Nome/substring do projeto                     |
| `--ambiente`    | ❌           | Filtra pelo nome do grupo contendo o ambiente |
| `--salvar`      | ❌           | Caminho do arquivo texto                      |
| `--out`         | ❌           | Exibir variáveis no terminal                  |

---

## 📦 Saída

* **pesquisar** e **listar** → lista:

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

## 📚 Boas práticas aplicadas

* Arquitetura limpa (Clean Code & SOLID)
* Fachada `AzureDevOps`, funções puras e separação clara de responsabilidades
* **Docstrings + type hints** para fácil manutenção
* **Zero dependências externas** além da stdlib do Python

---

## 🚀 Roadmap

* Exportar também para JSON ou YAML
* Suporte a múltiplas libs no comando `baixar`
* Melhorar a performance em grandes organizações

---

## ⚡ Instalação rápida via GitHub

```bash
git clone https://github.com/4lessandrodev/capivarinha-cli.git && \
cd capivarinha-cli && \
make instalar && \
cd .. && rm -rf capivarinha-cli
```
