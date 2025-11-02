import os
import sys

# importar cores
__path__ = os.path.abspath(os.path.dirname(__file__))
if __path__ not in sys.path:
    sys.path.append(__path__)
from cli.collor import yellow, green_bold, red_bold, blue_bold, cyan_bold
from commands import init as init_cmd, Camprint, Save, New, Hub, Duple

# Importar ChromaBuddy
try:
    chromabuddy_path = os.path.join(__path__, 'ChromaBuddy')
    if chromabuddy_path not in sys.path:
        sys.path.insert(0, chromabuddy_path)
    from ChromaBuddy.chat import ChromaBuddyPro
    from ChromaBuddy.core.config import ConfigManager
    from ChromaBuddy.core.ui import get_ui, get_logger
    from ChromaBuddy.models.cohe import generate
    CHROMABUDDY_AVAILABLE = True
except ImportError as e:
    CHROMABUDDY_AVAILABLE = False
    CHROMABUDDY_ERROR = str(e)

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
    print()
    print(cyan_bold("assistente de IA:"))
    print("  buddy          - iniciar ChromaBuddy (assistente interativo)")
    print("  ask <pergunta> - fazer pergunta rápida ao assistente")
    print("  analyze <file> - analisar arquivo com IA")
    print("  gerardds       - gerar estrutura_projeto.json para o workspace atual")
    print()
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

# comando: buddy (ChromaBuddy interativo)
def cmd_buddy():
    if not CHROMABUDDY_AVAILABLE:
        print(red_bold("[ERRO] ChromaBuddy não disponível"))
        print(f"Detalhes: {CHROMABUDDY_ERROR}")
        return
    
    try:
        print(cyan_bold("\n=== ChromaBuddy PRO ==="))
        print("Assistente de Codificação com IA\n")
        
        # Carregar configuração
        config_path = os.path.join(__path__, 'ChromaBuddy', 'config.json')
        config = ConfigManager(config_path)
        
        # Verificar API key
        api_key = config.get_api_key()
        if not api_key:
            print(yellow("[AVISO] API key não configurada"))
            print("Configure em ChromaBuddy/config.json")
            return
        
        # Obter diretório de trabalho atual
        project_root = os.getcwd()
        
        # Gerar estrutura do projeto automaticamente
        estrutura_path = os.path.join(project_root, 'estrutura_projeto.json')
        if not os.path.exists(estrutura_path):
            print(yellow(f"Analisando workspace: {project_root}"))
            print(yellow("Gerando estrutura do projeto... (isso pode levar alguns segundos)"))
            
            try:
                from ChromaBuddy.locate.dds import cltdds
                import json
                
                estrutura = cltdds(project_root, api_key)
                
                # Salvar estrutura
                with open(estrutura_path, 'w', encoding='utf-8') as f:
                    json.dump(estrutura, f, indent=2, ensure_ascii=False)
                
                num_arquivos = len(estrutura.get('estrutura', []))
                print(green_bold(f"✓ Estrutura gerada! {num_arquivos} arquivos analisados.\n"))
            except Exception as e:
                print(yellow(f"[AVISO] Não foi possível gerar estrutura completa: {e}"))
                print(yellow("Continuando sem estrutura (funcionalidade limitada).\n"))
        else:
            print(green_bold(f"✓ Usando estrutura existente: {estrutura_path}\n"))
        
        # Inicializar ChromaBuddy
        buddy = ChromaBuddyPro(config, project_root)
        
        print(green_bold("ChromaBuddy iniciado. Digite /help para ver comandos."))
        print(yellow("Digite 'exit' ou pressione Ctrl+C para sair.\n"))
        
        # Loop interativo
        while True:
            try:
                user_input = input(cyan_bold("buddy> ")).strip()
                
                if user_input.lower() in ('exit', 'quit', 'sair'):
                    print(green_bold("\nAté logo!"))
                    break
                
                if not user_input:
                    continue
                
                # Processar comando
                result = buddy.process_command(user_input)
                
                if result.get('error'):
                    print(red_bold(f"[ERRO] {result['error']}"))
                elif result.get('response'):
                    print(result['response'])
                
            except KeyboardInterrupt:
                print(green_bold("\n\nAté logo!"))
                break
            except EOFError:
                break
                
    except Exception as e:
        print(red_bold(f"[ERRO] Falha ao iniciar ChromaBuddy: {e}"))

# comando: ask (pergunta rápida ao assistente)
def cmd_ask(args):
    if not CHROMABUDDY_AVAILABLE:
        print(red_bold("[ERRO] ChromaBuddy não disponível"))
        return
    
    if not args:
        print(red_bold("[ERRO] Uso: ask <sua pergunta>"))
        return
    
    try:
        question = ' '.join(args)
        
        # Carregar configuração
        config_path = os.path.join(__path__, 'ChromaBuddy', 'config.json')
        config = ConfigManager(config_path)
        api_key = config.get_api_key()
        
        if not api_key:
            print(red_bold("[ERRO] API key não configurada"))
            return
        
        print(yellow(f"\nPergunta: {question}"))
        print(cyan_bold("Processando...\n"))
        
        # Gerar resposta
        system_prompt = "Você é um assistente útil para desenvolvimento de software. Responda de forma clara e concisa."
        resposta = generate(api_key, system_prompt, question)
        
        print(green_bold("Resposta:"))
        print(resposta)
        print()
        
    except Exception as e:
        print(red_bold(f"[ERRO] {e}"))

# comando: analyze (analisar arquivo com IA)
def cmd_analyze(args):
    if not CHROMABUDDY_AVAILABLE:
        print(red_bold("[ERRO] ChromaBuddy não disponível"))
        return
    
    if not args:
        print(red_bold("[ERRO] Uso: analyze <arquivo>"))
        return
    
    try:
        file_path = ' '.join(args)
        
        if not os.path.exists(file_path):
            print(red_bold(f"[ERRO] Arquivo não encontrado: {file_path}"))
            return
        
        # Ler arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Carregar configuração
        config_path = os.path.join(__path__, 'ChromaBuddy', 'config.json')
        config = ConfigManager(config_path)
        api_key = config.get_api_key()
        
        if not api_key:
            print(red_bold("[ERRO] API key não configurada"))
            return
        
        print(cyan_bold(f"\nAnalisando: {file_path}"))
        print(yellow("Processando...\n"))
        
        # Gerar análise
        system_prompt = "Você é um especialista em análise de código. Analise o código fornecido e forneça insights sobre qualidade, possíveis melhorias e problemas."
        user_prompt = f"Analise este código:\n\n```\n{content}\n```"
        
        analise = generate(api_key, system_prompt, user_prompt)
        
        print(green_bold("Análise:"))
        print(analise)
        print()
        
    except Exception as e:
        print(red_bold(f"[ERRO] {e}"))

# comando: gerardds (gerar estrutura_projeto.json)
def cmd_gerardds():
    if not CHROMABUDDY_AVAILABLE:
        print(red_bold("[ERRO] ChromaBuddy não disponível"))
        return
    
    try:
        # Carregar configuração
        config_path = os.path.join(__path__, 'ChromaBuddy', 'config.json')
        config = ConfigManager(config_path)
        api_key = config.get_api_key()
        
        if not api_key:
            print(red_bold("[ERRO] API key não configurada"))
            print(yellow("Configure em ChromaBuddy/config.json"))
            return
        
        # Obter diretório de trabalho atual
        project_root = os.getcwd()
        estrutura_path = os.path.join(project_root, 'estrutura_projeto.json')
        
        print(cyan_bold("\n=== Gerador de Estrutura do Projeto ===\n"))
        print(yellow(f"Workspace: {project_root}"))
        print(yellow("Analisando arquivos... (isso pode levar alguns segundos)\n"))
        
        # Importar e executar cltdds
        from ChromaBuddy.locate.dds import cltdds
        import json
        
        # Gerar estrutura
        estrutura = cltdds(project_root, api_key)
        
        # Salvar estrutura
        with open(estrutura_path, 'w', encoding='utf-8') as f:
            json.dump(estrutura, f, indent=2, ensure_ascii=False)
        
        # Estatísticas
        num_arquivos = len(estrutura.get('estrutura', []))
        num_python = sum(1 for item in estrutura.get('estrutura', []) if item.get('arquivo', '').endswith('.py'))
        num_outros = num_arquivos - num_python
        
        print(green_bold("✓ Estrutura gerada com sucesso!\n"))
        print(f"  Arquivo: {estrutura_path}")
        print(f"  Total de arquivos analisados: {num_arquivos}")
        print(f"    - Arquivos Python: {num_python}")
        print(f"    - Outros arquivos: {num_outros}")
        print()
        print(green_bold("Agora você pode usar o comando 'buddy' com @mentions otimizados!"))
        print()
        
    except Exception as e:
        print(red_bold(f"[ERRO] Falha ao gerar estrutura: {e}"))
        import traceback
        print(yellow(traceback.format_exc()))

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
        elif cmd == "buddy":
            cmd_buddy()
        elif cmd == "ask":
            cmd_ask(args)
        elif cmd == "analyze":
            cmd_analyze(args)
        elif cmd == "gerardds":
            cmd_gerardds()
        else:
            print(yellow("[INFO]") + f" comando desconhecido: {cmd}. Use 'help'.")

if __name__ == "__main__":
    main()


