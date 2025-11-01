import os
import sys
import shutil

# importar cores
__path__ = os.path.abspath(os.path.dirname(__file__) + '/..')
sys.path.append(__path__)

from cli.collor import yellow, green_bold, red_bold
from utils.config import find_documents_folder

class Duple:
    def __init__(self, repo_name_or_path=None):
        self.chroma_folder = find_documents_folder()
        self.current_workspace = os.getcwd()
        self.repo_name = repo_name_or_path

    def normalize_path(self, path):
        """Normaliza o caminho, removendo aspas e convertendo barras"""
        if not path:
            return path
        
        # Remover aspas se presentes
        path = path.strip('"').strip("'")
        
        # Normalizar barras para o sistema operacional
        path = os.path.normpath(path)
        
        return path

    def find_repository_path(self, repo_input):
        """Encontra o caminho completo do repositório"""
        repo_input = self.normalize_path(repo_input)
        
        # Se já é um caminho absoluto
        if os.path.isabs(repo_input):
            # Se é um arquivo, pegar o diretório pai
            if os.path.isfile(repo_input):
                repo_path = os.path.dirname(repo_input)
            else:
                repo_path = repo_input
            
            if os.path.exists(repo_path) and os.path.isdir(repo_path):
                return repo_path
            else:
                return None
        
        # Se é um nome relativo, procura na pasta ChromaGithub
        repo_path = os.path.join(self.chroma_folder, repo_input)
        if os.path.exists(repo_path) and os.path.isdir(repo_path):
            return repo_path
        
        return None

    def get_repo_name_from_path(self, repo_path):
        """Extrai o nome do repositório do caminho"""
        return os.path.basename(repo_path)

    def copy_repository_to_workspace(self, source_path, dest_name):
        """Copia o repositório para o workspace atual"""
        dest_path = os.path.join(self.current_workspace, dest_name)
        
        # Verificar se já existe no destino
        if os.path.exists(dest_path):
            overwrite = input(f"'{dest_name}' já existe. Sobrescrever? (s/n): ").strip().lower()
            if overwrite not in ['s', 'sim', 'y', 'yes']:
                print(yellow("Operação cancelada"))
                return False
            
            # Remove a pasta existente
            try:
                shutil.rmtree(dest_path)
            except Exception as e:
                print(red_bold(f"Erro ao remover pasta existente: {e}"))
                return False
        
        # Copiar a pasta
        try:
            shutil.copytree(source_path, dest_path)
            return dest_path
        except Exception as e:
            print(red_bold(f"Erro ao copiar repositório: {e}"))
            return False

    def run(self):
        """Executa o comando duple"""
        if not self.repo_name:
            self.repo_name = input("Nome ou caminho do repositório: ").strip()
        
        if not self.repo_name:
            print(red_bold("Nome do repositório não pode ser vazio"))
            return
        
        # Encontrar o repositório
        repo_path = self.find_repository_path(self.repo_name)
        if not repo_path:
            print(red_bold(f"Repositório '{self.repo_name}' não encontrado"))
            return
        
        repo_name = self.get_repo_name_from_path(repo_path)
        
        print(green_bold(f"Encontrado: {repo_name}"))
        print(f"📁 {repo_path}")
        
        # Confirmar cópia
        confirm = input(f"Copiar para '{self.current_workspace}'? (s/n): ").strip().lower()
        if confirm not in ['s', 'sim', 'y', 'yes']:
            print(yellow("Operação cancelada"))
            return
        
        # Copiar
        result = self.copy_repository_to_workspace(repo_path, repo_name)
        if result:
            print(green_bold(f"✅ Repositório copiado para: {result}"))
        else:
            print(red_bold("❌ Falha ao copiar repositório"))

# função para uso rápido
def duple(repo_name=None):
    d = Duple(repo_name)
    d.run()