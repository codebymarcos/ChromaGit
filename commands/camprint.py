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

class Camprint:
    def __init__(self):
        # Usa o diretório atual como caminho
        self.path = os.getcwd()
    
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
            
        return invisible_folder

    # criar uma pasta do repositorio na pasta global ChromaGithub
    def create_repo_in_global_folder(self):
        """
        Cria ou localiza a pasta global ChromaGithub e cria o repositório dentro dela
        """
        # Primeiro tenta encontrar a pasta ChromaGithub existente
        path_global = locate_university_folder()
        
        # Se não encontrar, usa a função para criar na pasta Documents
        if not path_global:
            path_global = find_documents_folder()
            
        if not path_global:
            print(red_bold("Erro: Não foi possível encontrar ou criar a pasta ChromaGithub"))
            return None
            
        # Cria o repositório na pasta global
        return self.create_repo(path_global)
    
    def create_repo(self, path_global):
        """
        Cria ou atualiza um repositório na pasta global
        
        Args:
            path_global: Caminho da pasta ChromaGithub
            
        Returns:
            str: Caminho do repositório criado ou None em caso de erro
        """
        try:
            repo_name = os.path.basename(self.path)
            repo_path = os.path.join(path_global, repo_name)
            
            os.makedirs(repo_path, exist_ok=True)
            
            return repo_path
            
        except Exception as e:
            print(red_bold(f"[ERRO] Falha ao criar repositório: {str(e)}"))
            return None
    
    # copiar arquivos e pastas da pasta de controle para o repositorio na pasta global
    def copy_files_to_global_repo(self, repo_path, commit_message="Commit sem mensagem"):
        invisible_folder = self.locate_invisible_folder()
        if not invisible_folder:
            return
        
        try:
            files_copied = []
            for item in os.listdir(invisible_folder):
                s = os.path.join(invisible_folder, item)
                d = os.path.join(repo_path, item)
                
                try:
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                        files_copied.append(f"{item}/")
                    else:
                        shutil.copy2(s, d)
                        files_copied.append(item)
                except PermissionError:
                    print(red_bold(f"[AVISO] Permissão negada: {item}"))
            
        except Exception as e:
            print(red_bold(f"[ERRO] Falha ao copiar arquivos: {str(e)}"))
            return

        # Registrar o commit no log
        log_file = os.path.join(repo_path, "commit_log.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"commit {timestamp}\n")
            f.write("-" * 50 + "\n")
            f.write(f"data: {timestamp}\n")
            f.write(f"repo: {os.path.basename(repo_path)}\n")
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
    repo_path = camprint.create_repo_in_global_folder()
    
    if not repo_path:
        sys.exit(1)
    
    print(yellow("\nchromagit >") + " Commitando alterações...")
    camprint.copy_files_to_global_repo(repo_path, args.message)
    print(green_bold("[OK] Commit realizado com sucesso"))