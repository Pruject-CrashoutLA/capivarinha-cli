APP_NAME = capi-cli
SCRIPT   = capi-cli.py
INSTALL_PATH = /usr/local/bin/$(APP_NAME)

.PHONY: instalar desinstalar executar

instalar:
	@echo "📦 Instalando $(APP_NAME) em $(INSTALL_PATH)..."
	@chmod +x $(SCRIPT)
	@sudo cp $(SCRIPT) $(INSTALL_PATH)
	@echo "✔ Instalação concluída. Agora você pode usar o comando '$(APP_NAME)'."

desinstalar:
	@echo "🗑 Removendo $(APP_NAME) de $(INSTALL_PATH)..."
	@sudo rm -f $(INSTALL_PATH)
	@echo "✔ Desinstalação concluída."

executar:
	@echo "▶ Executando $(SCRIPT) localmente..."
	@python3 $(SCRIPT) $(ARGS)
