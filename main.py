import os
import sys

# importar cores
__path__ = os.path.abspath(os.path.dirname(__file__))
if __path__ not in sys.path:
    sys.path.append(__path__)
from cli.collor import yellow, green_bold, red_bold
from commands import init as init_cmd, Camprint, Save, New, Hub, Duple

# util: formatar prompt com nome da pasta atual
def prompt():
    cwd = os.getcwd()
    folder = os.path.basename(cwd) or cwd
    return f"{yellow('chromagit >')} {folder} $ "

# comando: cd
def cmd_cd(args):
    if not args:
        print(red_bold("[ERRO] Uso: cd <caminho>"))
        return
    path = args[0]
    try:
        os.chdir(path)
    except FileNotFoundError:
        print(red_bold("[ERRO] Caminho não encontrado"))
    except NotADirectoryError:
        print(red_bold("[ERRO] Não é um diretório"))
    except PermissionError:
        print(red_bold("[ERRO] Permissão negada"))

# comando: pwd
def cmd_pwd():
    print(os.getcwd())

# comando: help
def cmd_help():
    print("comandos:")
    print("  cd <pasta>     - mudar de diretório")
    print("  pwd            - mostrar diretório atual")
    print("  init [path]    - inicializar repositório ChromaGit")
    print("  new            - criar novo repositório em Documents/ChromaGithub")
    print("  hub            - explorar repositórios em Documents/ChromaGithub")
    print("  duple <repo>   - copiar repositório do ChromaGithub para workspace")
    print("  commit [-m msg]- copiar para área invisível e registrar log")
    print("  save           - salvar em Documents/ChromaGithub/<repo>")
    print("  help           - listar comandos")
    print("  exit | quit    - sair")

# comando: init (wrapper)
def cmd_init(args):
    path = args[0] if args else None
    init_cmd(path)

# comando: commit (usa Camprint)
def cmd_commit(args):
    # extrair mensagem simples: -m <msg>
    message = "Commit sem mensagem"
    if args:
        if args[0] in ("-m", "--message") and len(args) >= 2:
            message = " ".join(args[1:])
        else:
            message = " ".join(args)

    camprint = Camprint()
    if not camprint.locate_invisible_folder():
        return

    print(yellow("\nchromagit >") + " Commitando alterações...")

    try:
        ignore_patterns = [
            ".hub_*",
            ".git",
            ".git/**",
            "__pycache__",
            "*.pyc",
            ".vscode",
            "*.git",
        ]

        def should_ignore(name, full_path):
            invisible_folder = os.path.basename(camprint.invisible_folder)
            if name.startswith(".hub_") or invisible_folder in full_path:
                return True
            for pattern in ignore_patterns:
                if pattern.startswith("*."):
                    if name.endswith(pattern[2:]):
                        return True
                elif pattern.endswith("/**"):
                    base = pattern[:-3]
                    if name.startswith(base):
                        return True
                elif pattern.startswith("*"):
                    if name.endswith(pattern[1:]):
                        return True
                elif name == pattern or name.startswith(pattern + os.sep):
                    return True
            return False

        # limpar pasta invisível
        for item in os.listdir(camprint.invisible_folder):
            item_path = os.path.join(camprint.invisible_folder, item)
            try:
                if os.path.isdir(item_path):
                    import shutil
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            except PermissionError:
                print(yellow(f"[AVISO] Permissão negada ao limpar: {item}"))

        # copiar arquivos
        files_copied = []
        for item in os.listdir(camprint.path):
            item_path = os.path.join(camprint.path, item)
            if should_ignore(item, item_path):
                continue
            s = os.path.join(camprint.path, item)
            d = os.path.join(camprint.invisible_folder, item)
            try:
                import shutil
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                    files_copied.append(f"{item}/")
                else:
                    shutil.copy2(s, d)
                    files_copied.append(item)
            except PermissionError:
                print(yellow(f"[AVISO] Permissão negada: {item}"))

        camprint.save_commit_log(message, files_copied)
        print(green_bold("[OK] Commit realizado com sucesso"))
    except Exception as e:
        print(red_bold(f"[ERRO] {str(e)}"))

# comando: save (usa Save)
def cmd_save():
    s = Save()
    s.save()

# comando: new (usa New)
def cmd_new():
    n = New()
    n.create()

# comando: hub (usa Hub)
def cmd_hub():
    h = Hub()
    h.run()

# comando: duple (usa Duple)
def cmd_duple(args):
    repo_name = ' '.join(args) if args else None
    d = Duple(repo_name)
    d.run()

def main():
    # loop principal
    while True:
        try:
            line = input(prompt()).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        parts = line.split()
        cmd, args = parts[0], parts[1:]

        if cmd in ("exit", "quit"):
            break
        elif cmd == "cd":
            cmd_cd(args)
        elif cmd == "pwd":
            cmd_pwd()
        elif cmd == "help":
            cmd_help()
        elif cmd == "init":
            cmd_init(args)
        elif cmd in ("commit", "camprint"):
            cmd_commit(args)
        elif cmd == "save":
            cmd_save()
        elif cmd == "new":
            cmd_new()
        elif cmd == "hub":
            cmd_hub()
        elif cmd == "duple":
            cmd_duple(args)
        else:
            print(yellow("[INFO]") + f" comando desconhecido: {cmd}. Use 'help'.")

if __name__ == "__main__":
    main()


