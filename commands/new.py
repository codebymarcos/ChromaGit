# new => novo repositorio
import os
import sys
import urllib.request
import json

__path__ = os.path.abspath(os.path.dirname(__file__) + '/..')
sys.path.append(__path__)
from cli.collor import red_bold, green_bold, yellow
from utils.config import find_documents_folder

class New:
    def __init__(self):
        self.repo_name = None
        self.chroma_folder = find_documents_folder()
        self.gitignore_cache = {}

    def get_gitignore_template(self, language):
        """Baixa template de .gitignore do GitHub se não estiver em cache"""
        if language in self.gitignore_cache:
            return self.gitignore_cache[language]
        
        try:
            # Mapeamento de linguagens para nomes de arquivos no repositório github/gitignore
            lang_map = {
                'python': 'Python.gitignore',
                'java': 'Java.gitignore',
                'javascript': 'Node.gitignore',
                'cpp': 'C++.gitignore',
                'generic': None  # Para genérico, usamos um template simples
            }
            
            if language == 'generic':
                template = """# Arquivos a ignorar
# Adicione aqui os arquivos e pastas que deseja ignorar

# Logs
*.log
logs/

# Arquivos temporários
*.tmp
*.temp
temp/
tmp/

# Arquivos do sistema operacional
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Editor/IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Build/Compile
build/
dist/
*.exe
*.dll
*.so
*.dylib"""
            else:
                filename = lang_map.get(language)
                if not filename:
                    return "# Arquivos a ignorar\n"
                
                url = f"https://raw.githubusercontent.com/github/gitignore/main/{filename}"
                with urllib.request.urlopen(url) as response:
                    template = response.read().decode('utf-8')
            
            self.gitignore_cache[language] = template
            return template
            
        except Exception as e:
            print(yellow(f"[AVISO] Não foi possível baixar template para {language}: {e}"))
            return "# Arquivos a ignorar\n"

    def get_repo_name(self):
        while True:
            repo_name = input("Nome do repositório: ").strip()
            if repo_name:
                if os.path.exists(os.path.join(self.chroma_folder, repo_name)):
                    print(red_bold(f"[ERRO] Repositório '{repo_name}' já existe"))
                    continue
                self.repo_name = repo_name
                break
            else:
                print(red_bold("[ERRO] Nome do repositório não pode ser vazio"))

    def ask_initial_files(self):
        files = []
        
        # Perguntar sobre .gitignore
        gitignore_response = input("Deseja adicionar .gitignore? (s/n): ").strip().lower()
        if gitignore_response in ['s', 'sim', 'y', 'yes']:
            gitignore_type = self.choose_gitignore_type()
            files.append(('.gitignore', gitignore_type))
        
        # Perguntar sobre README
        readme_response = input("Deseja adicionar README.md? (s/n): ").strip().lower()
        if readme_response in ['s', 'sim', 'y', 'yes']:
            files.append('README.md')
        
        return files

    def choose_gitignore_type(self):
        print("Tipos de .gitignore disponíveis:")
        print("1. Python")
        print("2. Java")
        print("3. JavaScript")
        print("4. C++")
        print("5. Genérico")
        
        while True:
            choice = input("Escolha o tipo (1-5): ").strip()
            if choice == '1':
                return 'python'
            elif choice == '2':
                return 'java'
            elif choice == '3':
                return 'javascript'
            elif choice == '4':
                return 'cpp'
            elif choice == '5':
                return 'generic'
            else:
                print(red_bold("[ERRO] Escolha uma opção válida (1-5)"))

    def create_repo_folder(self):
        repo_path = os.path.join(self.chroma_folder, self.repo_name)
        os.makedirs(repo_path, exist_ok=True)
        print(green_bold(f"[SUCESSO] Repositório '{self.repo_name}' criado em {repo_path}"))
        return repo_path

    def add_initial_files(self, repo_path, files):
        for file in files:
            if isinstance(file, tuple):
                file_name, file_type = file
            else:
                file_name = file
                file_type = None
            
            file_path = os.path.join(repo_path, file_name)
            if file_name == '.gitignore':
                content = self.get_gitignore_template(file_type)
                with open(file_path, 'w') as f:
                    f.write(content)
            elif file_name == 'README.md':
                with open(file_path, 'w') as f:
                    f.write(f"# {self.repo_name}\n\nDescrição do projeto.\n")
            print(green_bold(f"[SUCESSO] Arquivo '{file_name}' criado"))

    def create(self):
        print("Criando novo repositório ChromaGit...")
        
        self.get_repo_name()
        
        initial_files = self.ask_initial_files()
        
        repo_path = self.create_repo_folder()
        
        if initial_files:
            self.add_initial_files(repo_path, initial_files)
        
        print(green_bold(f"[SUCESSO] Repositório '{self.repo_name}' criado com sucesso!"))

# função para uso rápido
def new():
    n = New()
    n.create()