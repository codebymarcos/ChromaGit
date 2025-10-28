import os
import sys
import shutil

# importar cores
__path__ = os.path.abspath(os.path.dirname(__file__) + '/..')
sys.path.append(__path__)
from cli.collor import red_bold, green_bold, yellow
from utils.ignore import process_gitignore_folder

class Init:
    def __init__(self, path):
        self.path = path

    # criar uma pasta invisivel no workspace atual
    def create_invisible_folder(self):
        # Pega apenas o nome da pasta atual
        current_folder = os.path.basename(self.path)
        invisible_folder = os.path.join(self.path, f".hub_{current_folder}")
        os.makedirs(invisible_folder, exist_ok=True)
        return invisible_folder
    
    # verificar se a pasta invisivel existe
    def check_invisible_folder(self):
        current_folder = os.path.basename(self.path)
        invisible_folder = os.path.join(self.path, f".hub_{current_folder}")
        return os.path.exists(invisible_folder)
    
    # processar arquivos usando a nova funcao de ignore
    def process_files_with_gitignore(self):
        # cria a pasta invisivel primeiro
        invisible_folder = self.create_invisible_folder()
        
        # adiciona padrao para ignorar a pasta invisivel
        current_folder = os.path.basename(self.path)
        invisible_pattern = f".hub_{current_folder}"
        
        # usa a funcao integrada do utils/ignore.py
        return process_gitignore_folder(self.path, invisible_folder, ignore_patterns=[invisible_pattern])

    # copiar arquivos do workspace atual para a pasta invisivel
    def copy_files_to_invisible_folder(self):
        # redireciona para o novo metodo
        return self.process_files_with_gitignore()

# função para uso rapido
def init(path=None):
    """
    Inicializa um repositório ChromaGit no diretório especificado ou no diretório atual.
    
    Args:
        path (str, optional): Caminho para o diretório onde inicializar. 
                            Se não fornecido, usa o diretório atual.
    
    Returns:
        bool: True se a inicialização foi bem sucedida, False caso contrário.
    """
    try:
        if path is None:
            path = os.getcwd()
        
        init_cmd = Init(path)
        print(yellow("\nchromagit >") + f" Inicializando repositório em: {path}")
        
        # Cria e verifica a pasta de controle
        invisible_folder = init_cmd.create_invisible_folder()
        if not init_cmd.check_invisible_folder():
            print(red_bold("[ERRO] Falha ao criar pasta de controle"))
            return False
        
        # Copia os arquivos respeitando o .gitignore
        try:
            init_cmd.copy_files_to_invisible_folder()
            print(green_bold("[OK] Repositório inicializado com sucesso"))
            return True
            
        except Exception as e:
            print(red_bold(f"[ERRO] {str(e)}"))
            return False
        
    except Exception as e:
        print(red_bold(f"[ERRO] {str(e)}"))
        return False

# testar a classe
if __name__ == "__main__":
    if init():
        sys.exit(0)
    else:
        sys.exit(1)