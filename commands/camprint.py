# camprint => commit
from datetime import datetime
import os
import sys
import shutil

# Para capturar argumentos da linha de comando
import argparse   

# importar cores
__path__ = os.path.abspath(os.path.dirname(__file__) + '/..')
sys.path.append(__path__)
from cli.collor import *
from utils.config import find_documents_folder, locate_university_folder
from cli.progress import ProgressLogger

class Camprint:
    def __init__(self):
        # Usa o diretório atual como caminho
        self.path = os.getcwd()
        self.invisible_folder = None
    
    # procurar a pasta .hub_<nome do repositorio> no workspace atual
    def locate_invisible_folder(self):
        if not self.path:
            print(red_bold("[ERRO] Diretório de trabalho não encontrado"))
            return None
            
        current_folder = os.path.basename(self.path)
        invisible_folder = os.path.join(self.path, f".hub_{current_folder}")
        
        if not os.path.exists(invisible_folder):
            print(red_bold("[ERRO] Repositório não inicializado"))
            print(red_bold("[INFO] Execute: chromagit init"))
            return None
            
        self.invisible_folder = invisible_folder
        return invisible_folder

    # Funções relacionadas ao push serão movidas para um novo arquivo push.py
    
    def save_commit_log(self, commit_message="Commit sem mensagem", files_copied=None):
        """
        Salva o log do commit na pasta invisível
        """
        if not files_copied:
            files_copied = []
            
        # Registrar o commit no log
        log_file = os.path.join(self.invisible_folder, "commit_log.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"commit {timestamp}\n")
            f.write("-" * 50 + "\n")
            f.write(f"data: {timestamp}\n")
            f.write(f"repo: {os.path.basename(self.path)}\n")
            f.write(f"\n{commit_message}\n\n")
            f.write("arquivos alterados:\n")
            for file in sorted(files_copied):
                f.write(f"  {file}\n")
            f.write("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executa o commit no ChromaGit")
    parser.add_argument("-m", "--message", type=str, 
                       help="Mensagem do commit", 
                       default="Commit sem mensagem")
    args = parser.parse_args()
    
    camprint = Camprint()
    
    # Localiza e verifica a pasta invisível
    if not camprint.locate_invisible_folder():
        sys.exit(1)
    
    print(yellow("\nchromagit >") + " Commitando alterações...")
    
    try:
        # Lista de padrões para ignorar
        ignore_patterns = [
            ".hub_*",         # Nossas pastas invisíveis e seus conteúdos
            ".git",           # Pasta git
            ".git/**",        # Todos os arquivos dentro de .git
            "__pycache__",    # Cache Python
            "*.pyc",          # Arquivos compilados Python
            ".vscode",        # Configurações VS Code
            "*.git",          # Qualquer arquivo .git
        ]
        
        # Função auxiliar para verificar se deve ignorar
        def should_ignore(name, full_path):
            # Primeiro verifica se é a pasta invisível ou está dentro dela
            invisible_folder = os.path.basename(camprint.invisible_folder)
            if name.startswith(".hub_") or invisible_folder in full_path:
                return True
                
            # Depois verifica os outros padrões
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
            
        # Primeiro define itens a copiar (aplica filtro)
        items_to_copy = []
        for item in os.listdir(camprint.path):
            item_path = os.path.join(camprint.path, item)
            if should_ignore(item, item_path):
                continue
            items_to_copy.append(item)

        # Depois limpa a pasta invisível
        for item in os.listdir(camprint.invisible_folder):
            item_path = os.path.join(camprint.invisible_folder, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            except PermissionError:
                print(yellow(f"[AVISO] Permissão negada ao limpar: {item}"))
        
        # Depois copia os novos arquivos com barra de progresso
        files_copied = []
        with ProgressLogger("Copiando arquivos para área invisível...", total=len(items_to_copy)) as p:
            for item in items_to_copy:
                s = os.path.join(camprint.path, item)
                d = os.path.join(camprint.invisible_folder, item)
                try:
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                        files_copied.append(f"{item}/")
                    else:
                        shutil.copy2(s, d)
                        files_copied.append(item)
                except PermissionError:
                    print(yellow(f"[AVISO] Permissão negada: {item}"))
                finally:
                    p.update(1, custom_message=item)
                
        # Salva o log do commit
        camprint.save_commit_log(args.message, files_copied)
        print(green_bold("[OK] Commit realizado com sucesso"))
        
    except Exception as e:
        print(red_bold(f"[ERRO] {str(e)}"))
        sys.exit(1)