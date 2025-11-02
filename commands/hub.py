# hub.py => mostrar os repositorios na pasta ChromaGithub
import os
import sys

__path__ = os.path.abspath(os.path.dirname(__file__) + '/..')
sys.path.append(__path__)
from cli.collor import red_bold, green_bold, yellow
from utils.config import find_documents_folder
from .noctis_map import scan_map, view_map, ide_map

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

    def view_repository(self, repo_name):
        """Visualiza a estrutura do repositório usando noctis_map"""
        repo_path = os.path.join(self.chroma_folder, repo_name)
        if not os.path.exists(repo_path):
            print(red_bold(f"Repositório '{repo_name}' não encontrado"))
            return
        print(green_bold(f"Visualizando estrutura de {repo_name}"))
        view_map(repo_path)

    def scan_repository(self, repo_name):
        """Escaneia o conteúdo do repositório usando noctis_map"""
        repo_path = os.path.join(self.chroma_folder, repo_name)
        if not os.path.exists(repo_path):
            print(red_bold(f"Repositório '{repo_name}' não encontrado"))
            return
        print(green_bold(f"Escaneando conteúdo de {repo_name}"))
        scan_map(repo_path)

    def edit_file_in_repository(self, repo_name):
        """Permite editar um arquivo no repositório usando noctis_map IDE"""
        repo_path = os.path.join(self.chroma_folder, repo_name)
        if not os.path.exists(repo_path):
            print(red_bold(f"Repositório '{repo_name}' não encontrado"))
            return
        
        # Listar arquivos na raiz para escolher
        try:
            files = [f for f in os.listdir(repo_path) if os.path.isfile(os.path.join(repo_path, f))]
            if not files:
                print(yellow("Nenhum arquivo encontrado na raiz"))
                return
            
            print("Arquivos disponíveis:")
            for i, file in enumerate(files, 1):
                print(f"{i}. {file}")
            
            choice = input("Selecione um arquivo (número) ou 'cancelar': ").strip()
            if choice.lower() in ['cancelar', 'c']:
                return
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(files):
                    file_path = os.path.join(repo_path, files[index])
                    print(green_bold(f"Editando {files[index]}"))
                    ide_map(file_path)
                else:
                    print(red_bold("Número inválido"))
            except ValueError:
                print(red_bold("Digite um número válido"))
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
                
                # Menu de ações
                while True:
                    print("\nAções disponíveis:")
                    print("1. Visualizar estrutura (árvore)")
                    print("2. Escanear conteúdo (gerar .md)")
                    print("3. Editar arquivo")
                    print("4. Ver outro repositório")
                    print("5. Sair")
                    
                    choice = input("Escolha uma ação (1-5): ").strip()
                    
                    if choice == '1':
                        self.view_repository(selected_repo)
                    elif choice == '2':
                        self.scan_repository(selected_repo)
                    elif choice == '3':
                        self.edit_file_in_repository(selected_repo)
                    elif choice == '4':
                        break
                    elif choice == '5':
                        return
                    else:
                        print(red_bold("Opção inválida"))
            else:
                break

# função para uso rápido
def hub():
    h = Hub()
    h.run()