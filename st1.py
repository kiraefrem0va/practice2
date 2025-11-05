import sys
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

def check_repository(repo):
    if repo.startswith(("http://", "https://")):
        return
    path = Path(repo)
    if not path.exists():
        raise FileNotFoundError(f"Файл или директория '{repo}' не найдены")

def check_package_version(version):
    if not any(c.isdigit() for c in version):
        raise ValueError("Версия пакета должна содержать цифры (например, 1.0.0)")

def check_output_file(filename):
    if not filename.endswith((".png", ".jpg", ".svg")):
        raise ValueError("Имя выходного файла должно заканчиваться на .png/.jpg/.svg")

def main():
    try:
        args = parse_args()

        check_repository(args["repository_url"])
        check_package_version(args["package_version"])
        check_output_file(args["output_file"])

    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    print("\nПараметры конфигурации:")
    for key, value in args.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()