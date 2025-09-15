# ============================================================
# Makefile para capi-cli
# ============================================================

APP_NAME   = capi-cli
SCRIPT     = capi-cli.py

# Permite customizar via: make PREFIX=/opt instalar
PREFIX     = /usr/local
BIN_DIR    = $(PREFIX)/bin
INSTALL_PATH = $(BIN_DIR)/$(APP_NAME)

# Detecta o Python disponível (python3 > python)
PY := $(shell command -v python3 >/dev/null 2>&1 && echo python3 || echo python)

.PHONY: help instalar desinstalar executar verificar versao instalar-extensao

help:
	@echo "Comandos disponíveis:"
	@echo "  make instalar           -> instala '$(APP_NAME)' em '$(INSTALL_PATH)'"
	@echo "  make desinstalar        -> remove '$(APP_NAME)' de '$(INSTALL_PATH)'"
	@echo "  make executar ARGS='...'-> executa localmente o script com argumentos"
	@echo "  make verificar          -> checa Azure CLI e extensão azure-devops"
	@echo "  make versao             -> mostra a versão do $(APP_NAME)"
	@echo "  make instalar-extensao  -> instala a extensão azure-devops no az"
	@echo ""
	@echo "Exemplos:"
	@echo "  make instalar"
	@echo "  make executar ARGS='pesquisar --organizacao=https://dev.azure.com/minha-org --termo=test --out'"
	@echo "  make versao"

instalar:
	@echo "📦 Instalando $(APP_NAME) em $(INSTALL_PATH)..."
	@mkdir -p "$(BIN_DIR)"
	@chmod +x "$(SCRIPT)"
	@install -m 0755 "$(SCRIPT)" "$(INSTALL_PATH)"
	@echo "✔ Instalação concluída. Agora você pode usar o comando '$(APP_NAME)'."
	@echo "ℹ Dica: execute '$(APP_NAME) --version' para validar."

desinstalar:
	@echo "🗑 Removendo $(APP_NAME) de $(INSTALL_PATH)..."
	@rm -f "$(INSTALL_PATH)"
	@echo "✔ Desinstalação concluída."

executar:
	@if [ -z "$(ARGS)" ]; then \
		echo "⚠ Informe ARGS=\"...\". Ex.: make executar ARGS='--version'"; \
	else \
		echo "▶ Executando: $(PY) $(SCRIPT) $(ARGS)"; \
		"$(PY)" "$(SCRIPT)" $(ARGS); \
	fi

verificar:
	@echo "🔎 Verificando dependências..."
	@command -v az >/dev/null 2>&1 && echo "✔ Azure CLI encontrada" || (echo "❌ Azure CLI não encontrada. Instale e rode 'az login'."; exit 1)
	@az extension list -o tsv 2>/dev/null | grep -qi azure-devops && echo "✔ Extensão azure-devops instalada" || echo "⚠ Extensão azure-devops não encontrada (use 'make instalar-extensao')"
	@echo "✔ Verificação concluída."

versao:
	@echo "ℹ Versão pelo script local:"
	@"$(PY)" "$(SCRIPT)" --version || true
	@echo "ℹ Versão do comando instalado (se existir):"
	@command -v "$(APP_NAME)" >/dev/null 2>&1 && "$(APP_NAME)" --version || echo "  (comando ainda não instalado)"

instalar-extensao:
	@echo "🔧 Instalando extensão azure-devops no Azure CLI..."
	@az extension add --name azure-devops || (echo "❌ Falha ao instalar extensão azure-devops."; exit 1)
	@echo "✔ Extensão instalada."
