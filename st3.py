import sys
import json
import urllib.request
from pathlib import Path

def parse_args():
    args = {
        "package_name": None,
        "repository_url": None,
        "test_repo_mode": None,
        "package_version": None,
        "output_file": None
    }

    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--package-name":
            i += 1
            if i >= len(argv):
                raise ValueError("Ошибка: --package-name требует значение")
            args["package_name"] = argv[i]
        elif arg == "--repository-url":
            i += 1
            if i >= len(argv):
                raise ValueError("Ошибка: --repository-url требует значение")
            args["repository_url"] = argv[i]
        elif arg == "--test-repo-mode":
            i += 1
            if i >= len(argv):
                raise ValueError("Ошибка: --test-repo-mode требует значение")
            if argv[i] not in ("local", "remote"):
                raise ValueError("Ошибка: --test-repo-mode должен быть 'local' или 'remote'")
            args["test_repo_mode"] = argv[i]
        elif arg == "--package-version":
            i += 1
            if i >= len(argv):
                raise ValueError("Ошибка: --package-version требует значение")
            args["package_version"] = argv[i]
        elif arg == "--output-file":
            i += 1
            if i >= len(argv):
                raise ValueError("Ошибка: --output-file требует значение")
            args["output_file"] = argv[i]
        else:
            raise ValueError(f"Ошибка: неизвестный аргумент '{arg}'")
        i += 1

    missing = [k for k, v in args.items() if not v]
    if missing:
        raise ValueError(f"Ошибка: отсутствуют обязательные параметры: {', '.join(missing)}")

    return args

def check_repository(repo, mode):
    if mode == "remote":
        if not repo.startswith(("http://", "https://")):
            raise ValueError("Для remote-режима требуется URL репозитория")
    else:
        path = Path(repo)
        if not path.exists():
            raise FileNotFoundError(f"Файл или директория '{repo}' не найдены")

def check_package_version(version):
    if not any(c.isdigit() for c in version):
        raise ValueError("Версия пакета должна содержать цифры")

def check_output_file(filename):
    if not filename.endswith((".tar.gz", ".whl")):
        raise ValueError("Имя выходного файла должно заканчиваться на .tar.gz или .whl")

def load_local_graph(path):
    graph = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            package, deps = line.split(":", 1)
            deps_list = deps.split() if deps.strip() else []
            graph[package.strip()] = deps_list
    return graph

def load_remote_graph(package_name, version):
    url = f"https://pypi.org/pypi/{package_name}/{version}/json"
    print(f"Получаем информацию о пакете {package_name} по адресу: {url}")
    try:
        with urllib.request.urlopen(url) as response:
            data = json.load(response)
    except Exception as e:
        raise RuntimeError(f"Не удалось получить данные с {url}: {e}")

    requires = data["info"].get("requires_dist")
    if not requires:
        return {package_name: []}

    deps = []
    for dep in requires:
        dep_name = dep.split(";")[0].split()[0]
        deps.append(dep_name)
    return {package_name: deps}

def get_transitive_dependencies(graph, start):
    visited = set()
    stack = [start]
    result = set()

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for dep in graph.get(node, []):
            if dep not in result:
                result.add(dep)
                stack.append(dep)
    return result

def main():
    try:
        args = parse_args()
        check_repository(args["repository_url"], args["test_repo_mode"])
        check_package_version(args["package_version"])
        check_output_file(args["output_file"])

        if args["test_repo_mode"] == "local":
            graph = load_local_graph(args["repository_url"])
        else:
            graph = load_remote_graph(args["package_name"], args["package_version"])

        print("\nГраф зависимостей:")
        for pkg, deps in graph.items():
            print(f"{pkg}: {deps}")

        transitive = get_transitive_dependencies(graph, args["package_name"])
        print(f"\nТранзитивные зависимости пакета {args['package_name']}:")
        if transitive:
            for dep in sorted(transitive):
                print(f" - {dep}")
        else:
            print(" (нет зависимостей)")

    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()