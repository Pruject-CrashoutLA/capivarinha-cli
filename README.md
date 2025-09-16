# 🐾 Capivarinha CLI (`capi-cli`)

Uma CLI em **Python puro** para interagir com **Variable Groups** do Azure DevOps.

![Capivarinha executando um comando Azure](banner.jpg)

---

## ✨ Funcionalidades

* 🔍 **Pesquisar**: encontra variáveis cujo **valor** contém um termo informado.  
* 📥 **Baixar**: exporta todas as variáveis de um **Variable Group (lib)** para um arquivo `.env`.  
* 📂 **Listar**: exibe os **grupos (libs)** disponíveis por projeto/ambiente, **sem variáveis**.  
* 🔀 **Comparar**: compara **duas libs** e mostra as variáveis **exclusivas** de cada uma.

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

### Listar (somente grupos/libs)

```bash
capi-cli listar \
  --organizacao=https://dev.azure.com/minha-org \
  --projeto=BOARD --ambiente=DEV \
  --salvar=grupos.txt --out
```

### Comparar (duas libs)

```bash
capi-cli comparar \
  --organizacao=https://dev.azure.com/minha-org \
  --projeto=BOARD \
  --lib Meu-App.Backend.DEV \
  --lib Meu-App.Backend.QAS \
  --out
```

Saída de exemplo:

```
------ DEV -------
+ HOST=localhost:300 (Existe em DEV mas não existe em QAS)
------ QAS -------
+ PORT=3000 (Existe em QAS mas não existe em DEV)
------------------
```

---

## 🔧 Comandos e parâmetros

### 🔍 `pesquisar`

| Parâmetro       | Obrigatório | Descrição                                                   |
| --------------- | ----------- | ----------------------------------------------------------- |
| `--organizacao` | ✅           | URL da organização (ex.: `https://dev.azure.com/minha-org`) |
| `--termo`       | ✅           | Termo a ser buscado nos valores                             |
| `--projeto`     | ❌           | Filtro por nome/substring de projeto                        |
| `--ambiente`    | ❌           | Filtra pelo nome do grupo (ex.: `DEV`, `QAS`, etc.)         |
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

### 📂 `listar` (somente grupos/libs)

| Parâmetro       | Obrigatório | Descrição                                     |
| --------------- | ----------- | --------------------------------------------- |
| `--organizacao` | ✅           | URL da organização                            |
| `--projeto`     | ❌           | Nome/substring do projeto                     |
| `--ambiente`    | ❌           | Filtra pelo nome do grupo contendo o ambiente |
| `--salvar`      | ❌           | Caminho do arquivo texto                      |
| `--out`         | ❌           | Exibir lista no terminal                      |

> A saída lista **apenas** `Projeto`, `Grupo`, `Criado por` e `Modificado por`, sem variáveis.

---

### 🔀 `comparar`

| Parâmetro       | Obrigatório | Descrição                                                                |
| --------------- | ----------- | ------------------------------------------------------------------------ |
| `--organizacao` | ✅           | URL da organização                                                       |
| `--projeto`     | ❌           | Nome/substring do projeto                                                |
| `--lib`         | ✅ (×2)      | Informe **duas vezes**: primeira e segunda lib (match exato > substring) |
| `--ambiente`    | ❌           | Filtra pelo nome do grupo contendo o ambiente                            |
| `--salvar`      | ❌           | Caminho do arquivo texto para salvar a comparação                        |
| `--out`         | ❌           | Exibir comparação no terminal                                            |

> A comparação mostra as **variáveis exclusivas** de cada lib. (Opcionalmente, você pode salvar essa saída em um arquivo via `--salvar`.)

---

## 📦 Saída

* **pesquisar** → lista:

  ```
  projeto | grupo | chave | valor | criado_por | modificado_por
  ```
* **listar** → lista **apenas** grupos/libs:

  ```
  --------------------------------------------------------------------------------
  Projeto: NOME_PROJETO
  Grupo:   NOME_DO_GRUPO
  Criado:  Nome <email>
  Modif.:  Nome <email>
  --------------------------------------------------------------------------------
  ```
* **baixar** → gera `.env`:

  ```
  KEY=VALUE
  ```

> 🔒 **Segredos** não são retornados pela Azure CLI — aparecem como `***SECRET***`.

---

## 🖥️ Experiência no terminal

* **Spinners discretos** (`Listando projetos...`, `Analisando grupos...`)
* Linha limpa ao final → saída organizada

---

## ⚠️ Limitações atuais

* Busca é **case-sensitive** por padrão (use `--ignore-case` para ignorar).
* Segredos não podem ser exportados (limitação da Azure CLI).

---

## 📚 Boas práticas aplicadas

* Arquitetura limpa (Clean Code & SOLID)
* Fachada `AzureDevOps`, funções puras e separação de responsabilidades
* **Docstrings + type hints** para manutenção simples
* **Zero dependências externas** além da stdlib do Python

---

## 🚀 Roadmap

* Exportar para JSON/YAML
* Suporte a múltiplas libs no `baixar`
* Mostrar diferenças de **valores** no `comparar` (quando a variável existe nas duas libs)
* Otimizações de performance em grandes organizações

---

## ⚡ Instalação rápida via GitHub

```bash
git clone https://github.com/4lessandrodev/capivarinha-cli.git && \
cd capivarinha-cli && \
make instalar && \
cd .. && rm -rf capivarinha-cli
```

---

## 🧾 Versão

```bash
capi-cli --version
```

Exemplo de saída: `v0.1.2`
