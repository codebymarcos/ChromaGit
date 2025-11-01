# hub.py => mostrar os repositorios na pasta ChromaGithub
import os
import sys

__path__ = os.path.abspath(os.path.dirname(__file__) + '/..')
sys.path.append(__path__)
from cli.collor import red_bold, green_bold, yellow
from utils.config import find_documents_folder

class Hub:
    def __init__(self):
        self.chroma_folder = find_documents_folder()

    def list_repositories(self):
        """Lista todos os repositórios na pasta ChromaGithub"""
        if not os.path.exists(self.chroma_folder):
            print(red_bold("[ERRO] Pasta ChromaGithub não encontrada"))
            return []
        
        repos = []
        try:
            for item in os.listdir(self.chroma_folder):
                item_path = os.path.join(self.chroma_folder, item)
                if os.path.isdir(item_path):
                    repos.append(item)
        except PermissionError:
            print(red_bold("[ERRO] Sem permissão para acessar a pasta ChromaGithub"))
            return []
        
        return sorted(repos)

    def print_repositories(self):
        """Exibe os repositórios disponíveis"""
        repos = self.list_repositories()
        if not repos:
            print(yellow("Nenhum repositório encontrado"))
            return
        
        print(green_bold("Repositórios:"))
        for i, repo in enumerate(repos, 1):
            print(f"{i}. {repo}")

    def select_repository(self):
        """Permite ao usuário selecionar um repositório"""
        repos = self.list_repositories()
        if not repos:
            return None
        
        while True:
            try:
                choice = input("Selecione um repositório (número) ou 'cancelar': ").strip()
                if choice.lower() in ['cancelar', 'c', 'quit', 'q']:
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(repos):
                    return repos[index]
                else:
                    print(red_bold(f"[ERRO] Escolha um número entre 1 e {len(repos)}"))
            except ValueError:
                print(red_bold("[ERRO] Digite um número válido"))

    def show_repository_info(self, repo_name):
        """Mostra informações detalhadas do repositório"""
        repo_path = os.path.join(self.chroma_folder, repo_name)
        
        if not os.path.exists(repo_path):
            print(red_bold(f"Repositório '{repo_name}' não encontrado"))
            return
        
        print(green_bold(f"\n{repo_name}"))
        print(f"Caminho: {repo_path}")
        
        # Contar arquivos
        total_files = 0
        total_dirs = 0
        
        try:
            for root, dirs, files in os.walk(repo_path):
                total_dirs += len(dirs)
                total_files += len(files)
            
            print(f"Total: {total_files} arquivos, {total_dirs} pastas")
            
            # Listar arquivos na raiz
            root_files = []
            root_dirs = []
            
            for item in os.listdir(repo_path):
                item_path = os.path.join(repo_path, item)
                if os.path.isfile(item_path):
                    root_files.append(item)
                elif os.path.isdir(item_path):
                    root_dirs.append(item)
            
            if root_files:
                print(f"\nArquivos na raiz:")
                for file in sorted(root_files):
                    print(f"  {file}")
            
            if root_dirs:
                print(f"\nPastas na raiz:")
                for folder in sorted(root_dirs):
                    print(f"  {folder}")
                
        except PermissionError:
            print(red_bold("Sem permissão para acessar os arquivos"))

    def run(self):
        """Executa o hub interativo"""
        print(green_bold("ChromaGit Hub"))
        
        repos = self.list_repositories()
        if not repos:
            print(yellow("Nenhum repositório encontrado"))
            return
        
        while True:
            self.print_repositories()
            
            selected_repo = self.select_repository()
            if selected_repo:
                self.show_repository_info(selected_repo)
                
                # Perguntar se quer ver outro
                again = input("\nVer outro? (s/n): ").strip().lower()
                if again not in ['s', 'sim', 'y', 'yes']:
                    break
            else:
                break

# função para uso rápido
def hub():
    h = Hub()
    h.run()