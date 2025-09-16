#!/usr/bin/env python3
from __future__ import annotations

"""
capi-cli

Uma CLI em Python (stdlib-only) para:
  1) pesquisar: localizar variáveis de ambiente (Variable Groups) que contenham um termo
  2) baixar: exportar as variáveis de um Variable Group específico para um arquivo .env
  3) listar: listar os Variable Groups (libs) aplicando filtros de projeto e ambiente
  4) comparar: comparar duas libs (grupos) e mostrar variáveis exclusivas de cada

Requisitos:
  - Python 3.8+
  - Azure CLI (az) instalada e autenticada: `az login`
  - (se necessário) extensão do Azure DevOps: `az extension add --name azure-devops`

Autor: 4lessandroDev
Versão: v0.1.3
"""

import argparse
import json
import os
import sys
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Set

VERSION = "v0.1.3"

# ==============================
# Utilidades de Console / Spinner
# ==============================
class Spinner:
    """Spinner simples para feedback visual sem poluir o terminal."""
    def __init__(self, message: str = "Processando...") -> None:
        self.message = message
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        # Fallback para terminais Windows antigos sem boa fonte unicode
        if os.name == "nt":
            self.frames = ["|", "/", "-", "\\"]
            self.interval = 0.12
        else:
            self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            self.interval = 0.08

    def __enter__(self) -> "Spinner":
        print(self.message, end=" ")
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.2)
        # limpa a linha do spinner
        print("\r" + " " * (len(self.message) + 2) + "\r", end="")

    def _spin(self) -> None:
        i = 0
        while not self._stop.is_set():
            sys.stdout.write(self.frames[i % len(self.frames)] + "\b")
            sys.stdout.flush()
            i += 1
            time.sleep(self.interval)


# ==============================
# Infra: execução de comandos az
# ==============================
class AzCliError(RuntimeError):
    """Erro ao executar comandos Azure CLI."""


def run_az(args: List[str]) -> Any:
    """Executa `az` com os argumentos fornecidos e retorna JSON parseado."""
    cmd = ["az"] + args + ["-o", "json"]
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as e:
        raise AzCliError(
            "Azure CLI não encontrada. Instale o `az` e faça login com `az login`."
        ) from e

    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        if "extension" in stderr.lower() and "azure-devops" in stderr.lower():
            raise AzCliError(
                f"{stderr}\nDica: tente instalar a extensão: az extension add --name azure-devops"
            )
        raise AzCliError(stderr or "Falha ao executar Azure CLI.")

    try:
        return json.loads(proc.stdout or "null")
    except json.JSONDecodeError as e:
        raise AzCliError("Retorno do Azure CLI não é um JSON válido.") from e


# ==============================
# Modelos de dados
# ==============================
@dataclass
class VariableGroup:
    id: int
    name: str
    variables: Dict[str, Dict[str, Any]]
    created_by: Dict[str, Any]
    modified_by: Dict[str, Any]

    @staticmethod
    def from_json(d: Dict[str, Any]) -> "VariableGroup":
        return VariableGroup(
            id=d.get("id"),
            name=d.get("name", ""),
            variables=d.get("variables", {}) or {},
            created_by=d.get("createdBy", {}) or {},
            modified_by=d.get("modifiedBy", {}) or {},
        )


# ==============================
# Azure DevOps Facade
# ==============================
class AzureDevOps:
    """Fachada para operações necessárias do Azure DevOps via Azure CLI."""
    def __init__(self, organization: str) -> None:
        self.organization = organization

    def list_projects(self) -> List[str]:
        data = run_az(["devops", "project", "list", "--organization", self.organization])
        values = data.get("value", []) if isinstance(data, dict) else []
        return [p.get("name") for p in values if p.get("name")]

    def list_variable_groups(self, project: str) -> List[VariableGroup]:
        data = run_az(
            [
                "pipelines",
                "variable-group",
                "list",
                "--organization",
                self.organization,
                "--project",
                project,
            ]
        )
        if not isinstance(data, list):
            return []
        return [VariableGroup.from_json(item) for item in data]


# ==============================
# Filtros e utilidades
# ==============================
def match_filter(value: str, needle: Optional[str]) -> bool:
    """Retorna True se `value` contém `needle` (case-sensitive) ou se não houver filtro."""
    if not needle:
        return True
    return needle in value


def contains(haystack: Optional[str], needle: str, ignore_case: bool = False) -> bool:
    """Retorna True se `haystack` contém `needle` (respeitando ignore_case)."""
    if haystack is None:
        return False
    if ignore_case:
        return needle.lower() in haystack.lower()
    return needle in haystack


def _extract_env_label(group_name: str) -> str:
    """Tenta extrair o sufixo de ambiente do nome do grupo (ex.: '... .DEV' -> 'DEV')."""
    if "." in group_name:
        return group_name.split(".")[-1]
    return group_name


# ==============================
# Casos de uso
# ==============================
def pesquisar(
    devops: AzureDevOps,
    termo: str,
    projeto: Optional[str],
    ambiente: Optional[str],
    ignore_case: bool,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    with Spinner("Listando projetos..."):
        projects = devops.list_projects()

    if projeto:
        projects = [p for p in projects if match_filter(p, projeto)]

    for proj in projects:
        with Spinner(f"Analisando grupos em: {proj}"):
            groups = devops.list_variable_groups(proj)

        for g in groups:
            if ambiente and (ambiente not in g.name):
                continue

            for k, meta in (g.variables or {}).items():
                raw_val = (meta or {}).get("value")
                val = str(raw_val) if raw_val is not None else None
                if contains(val, termo, ignore_case=ignore_case):
                    results.append(
                        {
                            "projeto": proj,
                            "grupo": g.name,
                            "variavel": k,
                            "valor": val,
                            "criado_por": _format_identity(g.created_by),
                            "modificado_por": _format_identity(g.modified_by),
                        }
                    )
    return results


def listar(
    devops: AzureDevOps,
    projeto: Optional[str],
    ambiente: Optional[str],
) -> List[Dict[str, Any]]:
    """Lista APENAS os Variable Groups (libs), sem variáveis, sem repetição."""
    results: List[Dict[str, Any]] = []
    seen: Set[Tuple[str, str]] = set()

    with Spinner("Listando projetos..."):
        projects = devops.list_projects()

    if projeto:
        projects = [p for p in projects if match_filter(p, projeto)]

    for proj in projects:
        with Spinner(f"Listando grupos em: {proj}"):
            groups = devops.list_variable_groups(proj)

        for g in groups:
            if ambiente and (ambiente not in g.name):
                continue

            key = (proj, g.name)
            if key in seen:
                continue
            seen.add(key)

            results.append(
                {
                    "projeto": proj,
                    "grupo": g.name,
                    "criado_por": _format_identity(g.created_by),
                    "modificado_por": _format_identity(g.modified_by),
                }
            )
    return results


def _find_group_in_projects(
    devops: AzureDevOps, projetos: List[str], lib_name: str, ambiente: Optional[str]
) -> Optional[Tuple[str, VariableGroup]]:
    """Procura um grupo por nome (exato > substring) nos projetos informados."""
    for proj in projetos:
        groups = devops.list_variable_groups(proj)
        exact = [g for g in groups if g.name == lib_name and (not ambiente or ambiente in g.name)]
        if exact:
            return proj, exact[0]
        partial = [g for g in groups if (lib_name in g.name) and (not ambiente or ambiente in g.name)]
        if partial:
            return proj, partial[0]
    return None


def comparar(
    devops: AzureDevOps,
    projeto: Optional[str],
    libs: List[str],
    ambiente: Optional[str],
) -> Tuple[Tuple[str, Dict[str, str]], Tuple[str, Dict[str, str]]]:
    """Compara duas libs (grupos) e retorna mapas .env de cada."""
    if len(libs) != 2:
        raise ValueError("Informe exatamente duas ocorrências de --lib para comparar.")

    with Spinner("Listando projetos..."):
        projects = devops.list_projects()

    if projeto:
        projects = [p for p in projects if match_filter(p, projeto)]
    if not projects:
        raise ValueError("Nenhum projeto encontrado com o filtro informado.")

    # Encontra a primeira lib
    found1 = _find_group_in_projects(devops, projects, libs[0], ambiente)
    if not found1:
        raise ValueError(f"Lib não encontrada: {libs[0]}")
    proj1, group1 = found1

    # Prioriza o mesmo projeto da primeira lib
    ordered_projects = [proj1] + [p for p in projects if p != proj1]
    found2 = _find_group_in_projects(devops, ordered_projects, libs[1], ambiente)
    if not found2:
        raise ValueError(f"Lib não encontrada: {libs[1]}")
    proj2, group2 = found2

    if proj1 != proj2:
        print(f"⚠ Aviso: as libs foram encontradas em projetos diferentes: '{proj1}' e '{proj2}'.")

    return (group1.name, _to_env_map(group1)), (group2.name, _to_env_map(group2))


def baixar(
    devops: AzureDevOps,
    projeto: str,
    lib: str,
    ambiente: Optional[str],
) -> Tuple[str, Dict[str, str]]:
    """Localiza um Variable Group por nome (lib) e retorna as variáveis para exportação .env."""
    with Spinner("Listando projetos..."):
        projects = devops.list_projects()

    cand_projects = [p for p in projects if match_filter(p, projeto)] if projeto else projects
    if not cand_projects:
        raise ValueError("Nenhum projeto encontrado com o filtro informado.")

    # Percorre projetos candidatos até achar a lib (match exato > substring)
    for proj in cand_projects:
        with Spinner(f"Procurando grupos em: {proj}"):
            groups = devops.list_variable_groups(proj)

        exact = [g for g in groups if g.name == lib and (not ambiente or ambiente in g.name)]
        if exact:
            g = exact[0]
            return g.name, _to_env_map(g)

        partial = [g for g in groups if (lib in g.name) and (not ambiente or ambiente in g.name)]
        if partial:
            g = partial[0]
            return g.name, _to_env_map(g)

    raise ValueError("Variable Group (lib) não encontrado nos projetos filtrados.")


# ==============================
# Helpers de formato e I/O
# ==============================
def _format_identity(identity: Dict[str, Any]) -> str:
    name = identity.get("displayName") or "Desconhecido"
    email = identity.get("uniqueName") or "Desconhecido"
    return f"{name} <{email}>"


def _to_env_map(group: VariableGroup) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for k, meta in (group.variables or {}).items():
        val = meta.get("value")
        if val is None:
            env[k] = "***SECRET***"
        else:
            env[k] = str(val)
    return env


def print_results(results: List[Dict[str, Any]]) -> None:
    if not results:
        print("Nenhum resultado encontrado.")
        return

    print("Resultados:\n" + "=" * 80)
    for r in results:
        print(
            f"Projeto: {r['projeto']}\n"
            f"Grupo:   {r['grupo']}\n"
            f"Chave:   {r['variavel']}\n"
            f"Valor:   {r['valor']}\n"
            f"Criado:  {r['criado_por']}\n"
            f"Modif.:  {r['modificado_por']}\n"
            + ("-" * 80)
        )


def print_groups(groups: List[Dict[str, Any]]) -> None:
    if not groups:
        print("Nenhum grupo encontrado.")
        return

    for g in groups:
        print("-" * 80)
        print(f"Projeto: {g['projeto']}")
        print(f"Grupo:   {g['grupo']}")
        print(f"Criado:  {g['criado_por']}")
        print(f"Modif.:  {g['modificado_por']}")
    print("-" * 80)


def print_comparison(
    left: Tuple[str, Dict[str, str]],
    right: Tuple[str, Dict[str, str]],
) -> None:
    """Imprime a comparação entre duas libs, mostrando variáveis exclusivas."""
    name1, env1 = left
    name2, env2 = right

    label1 = _extract_env_label(name1)
    label2 = _extract_env_label(name2)

    only_left = sorted(set(env1.keys()) - set(env2.keys()))
    only_right = sorted(set(env2.keys()) - set(env1.keys()))

    print(f"------ {label1} -------")
    if not only_left:
        print(f"(Sem variáveis exclusivas em {label1})")
    else:
        for k in only_left:
            print(f"+ {k}={env1[k]} (Existe em {label1} mas não existe em {label2})")

    print(f"------ {label2} -------")
    if not only_right:
        print(f"(Sem variáveis exclusivas em {label2})")
    else:
        for k in only_right:
            print(f"+ {k}={env2[k]} (Existe em {label2} mas não existe em {label1})")

    print("------------------")


def write_text_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def serialize_results_txt(results: List[Dict[str, Any]]) -> str:
    if not results:
        return "Nenhum resultado encontrado.\n"
    lines: List[str] = ["Resultados", "=" * 80]
    for r in results:
        lines.extend(
            [
                f"Projeto: {r['projeto']}",
                f"Grupo:   {r['grupo']}",
                f"Chave:   {r['variavel']}",
                f"Valor:   {r['valor']}",
                f"Criado:  {r['criado_por']}",
                f"Modif.:  {r['modificado_por']}",
                "-" * 80,
            ]
        )
    return "\n".join(lines) + "\n"


def serialize_groups_txt(groups: List[Dict[str, Any]]) -> str:
    if not groups:
        return "Nenhum grupo encontrado.\n"
    lines: List[str] = []
    for g in groups:
        lines.extend(
            [
                "-" * 80,
                f"Projeto: {g['projeto']}",
                f"Grupo:   {g['grupo']}",
                f"Criado:  {g['criado_por']}",
                f"Modif.:  {g['modificado_por']}",
            ]
        )
    lines.append("-" * 80)
    return "\n".join(lines) + "\n"


def serialize_env(env_map: Dict[str, str]) -> str:
    lines = [f"{k}={_quote_if_needed(v)}" for k, v in env_map.items()]
    return "\n".join(lines) + "\n"


def _quote_if_needed(value: str) -> str:
    if any(ch in value for ch in [' ', '#', '"', "'", '=', '$']):
        return "'" + value.replace("'", "'\"'\"'") + "'"
    return value


# ==============================
# CLI (argparse)
# ==============================
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="capi-cli",
        description="Busca, lista, exporta e compara variáveis dos Variable Groups (Azure DevOps)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    parser.add_argument(
        "--version", "-v",
        action="version",
        version=VERSION,
        help="Exibe a versão atual da ferramenta",
    )

    # pesquisar
    p_search = subparsers.add_parser(
        "pesquisar", help="Pesquisar variáveis cujo valor contenha um termo"
    )
    p_search.add_argument("--organizacao", required=True, help="URL da organização (ex.: https://dev.azure.com/minha-org)")
    p_search.add_argument("--termo", required=True, help="Termo obrigatório a ser buscado no valor das variáveis")
    p_search.add_argument("--projeto", help="Filtro opcional de projeto (substring)")
    p_search.add_argument("--ambiente", type=str.upper, help="Filtro opcional de ambiente (ex.: DEV, QAS, UAT, HTX, PRD ou qualquer outro)")
    p_search.add_argument("--ignore-case", action="store_true", help="Busca case-insensitive no valor das variáveis")
    p_search.add_argument("--salvar", help="Salvar resultados em arquivo de texto")
    p_search.add_argument("--out", action="store_true", help="Exibir resultados no terminal")

    # listar
    p_list = subparsers.add_parser("listar", help="Listar os Variable Groups (libs) disponíveis")
    p_list.add_argument("--organizacao", required=True, help="URL da organização (ex.: https://dev.azure.com/minha-org)")
    p_list.add_argument("--projeto", help="Filtro opcional de projeto (substring)")
    p_list.add_argument("--ambiente", type=str.upper, help="Filtro opcional de ambiente no nome do grupo")
    p_list.add_argument("--salvar", help="Salvar lista de grupos em arquivo texto")
    p_list.add_argument("--out", action="store_true", help="Exibir lista de grupos no terminal")

    # baixar
    p_download = subparsers.add_parser("baixar", help="Baixar as variáveis de um Variable Group (lib) para um .env")
    p_download.add_argument("--organizacao", required=True, help="URL da organização (ex.: https://dev.azure.com/minha-org)")
    p_download.add_argument("--projeto", required=True, help="Projeto (ou substring) onde está a lib")
    p_download.add_argument("--lib", required=True, help="Nome do Variable Group (lib). Ex.: Meu-App.QAS")
    p_download.add_argument("--ambiente", type=str.upper, help="Filtro opcional de ambiente no nome do grupo")
    p_download.add_argument("--salvar", help="Salvar .env no caminho indicado (ex.: .env)")
    p_download.add_argument("--out", action="store_true", help="Também exibir .env no terminal")

    # comparar
    p_compare = subparsers.add_parser("comparar", help="Comparar duas libs (grupos) e mostrar variáveis exclusivas")
    p_compare.add_argument("--organizacao", required=True, help="URL da organização (ex.: https://dev.azure.com/minha-org)")
    p_compare.add_argument("--projeto", help="Filtro opcional de projeto (substring)")
    p_compare.add_argument("--lib", action="append", required=True, help="Nome da lib (use duas vezes: --lib A --lib B)")
    p_compare.add_argument("--ambiente", type=str.upper, help="Filtro opcional de ambiente no nome do grupo")
    p_compare.add_argument("--out", action="store_true", help="Exibir comparação no terminal")
    p_compare.add_argument("--salvar", help="Salvar comparação em arquivo texto")

    return parser


# ==============================
# Entry point
# ==============================
def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    devops = AzureDevOps(organization=args.organizacao)

    if args.command == "pesquisar":
        try:
            results = pesquisar(devops, termo=args.termo, projeto=args.projeto, ambiente=args.ambiente, ignore_case=args.ignore_case)
        except AzCliError as e:
            print(f"❌ Azure CLI: {e}")
            return 2

        if args.salvar:
            write_text_file(args.salvar, serialize_results_txt(results))
            print(f"✔ Resultados salvos em: {args.salvar}")
        if args.out or not args.salvar:
            print_results(results)
        return 0

    if args.command == "listar":
        try:
            groups = listar(devops, projeto=args.projeto, ambiente=args.ambiente)
        except AzCliError as e:
            print(f"❌ Azure CLI: {e}")
            return 2

        if args.salvar:
            write_text_file(args.salvar, serialize_groups_txt(groups))
            print(f"✔ Grupos salvos em: {args.salvar}")
        if args.out or not args.salvar:
            print_groups(groups)
        return 0

    if args.command == "baixar":
        try:
            group_name, env_map = baixar(devops, projeto=args.projeto, lib=args.lib, ambiente=args.ambiente)
        except (ValueError, AzCliError) as e:
            print(f"❌ {e}")
            return 2

        env_text = serialize_env(env_map)
        if args.salvar:
            write_text_file(args.salvar, env_text)
            print(f"✔ .env salvo de '{group_name}' em: {args.salvar}")
        if args.out or not args.salvar:
            print(f"# {group_name}")
            print(env_text)
        return 0

    if args.command == "comparar":
        try:
            left, right = comparar(devops, projeto=args.projeto, libs=args.lib, ambiente=args.ambiente)
        except (ValueError, AzCliError) as e:
            print(f"❌ {e}")
            return 2

        # Serialização simples do diff para salvar (mesmo formato impresso)
        from io import StringIO
        buff = StringIO()
        name1, env1 = left
        name2, env2 = right
        label1 = _extract_env_label(name1)
        label2 = _extract_env_label(name2)
        only_left = sorted(set(env1.keys()) - set(env2.keys()))
        only_right = sorted(set(env2.keys()) - set(env1.keys()))
        buff.write(f"------ {label1} -------\n")
        if not only_left:
            buff.write(f"(Sem variáveis exclusivas em {label1})\n")
        else:
            for k in only_left:
                buff.write(f"+ {k}={env1[k]} (Existe em {label1} mas não existe em {label2})\n")
        buff.write(f"------ {label2} -------\n")
        if not only_right:
            buff.write(f"(Sem variáveis exclusivas em {label2})\n")
        else:
            for k in only_right:
                buff.write(f"+ {k}={env2[k]} (Existe em {label2} mas não existe em {label1})\n")
        buff.write("------------------\n")

        if args.salvar:
            write_text_file(args.salvar, buff.getvalue())
            print(f"✔ Comparação salva em: {args.salvar}")
        if args.out or not args.salvar:
            print_comparison(left, right)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
