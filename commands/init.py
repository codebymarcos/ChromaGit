import os
import sys
import shutil

# importar cores
__path__ = os.path.abspath(os.path.dirname(__file__) + '/..')
sys.path.append(__path__)
from cli.collor import red_bold, green_bold, yellow

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
    
    # Ler padrões do arquivo .gitignore
    def read_gitignore(self):
        gitignore_path = os.path.join(self.path, '.gitignore')
        patterns = []
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Ignora linhas vazias e comentários
                    if line and not line.startswith('#'):
                        patterns.append(line)
        return patterns

    # Verifica se um arquivo corresponde a um padrão do gitignore
    def matches_gitignore_pattern(self, filepath, pattern):
        import fnmatch
        from pathlib import Path

        # Converte o caminho para um objeto Path para facilitar a manipulação
        path = Path(filepath)
        relative_path = path.relative_to(Path(self.path))
        
        # Normaliza o padrão
        pattern = pattern.rstrip('/')  # Remove trailing slash
        
        # Casos especiais de padrões
        if pattern.startswith('*/'):
            # Padrão que corresponde a qualquer diretório
            pattern = pattern[2:]
            return any(part for part in relative_path.parts if fnmatch.fnmatch(part, pattern))
        elif pattern.startswith('**/'):
            # Padrão que corresponde a qualquer profundidade
            pattern = pattern[3:]
            return any(fnmatch.fnmatch(str(relative_path), f"*{pattern}"))
        elif pattern.startswith('/'):
            # Padrão absoluto (relativo à raiz do projeto)
            pattern = pattern[1:]
            return fnmatch.fnmatch(str(relative_path), pattern)
        else:
            # Padrão simples
            for part in relative_path.parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
            # Tenta corresponder ao caminho completo relativo
            return fnmatch.fnmatch(str(relative_path), pattern)

    # copiar arquivos do workspace atual para a pasta invisivel
    def copy_files_to_invisible_folder(self):
        current_folder = os.path.basename(self.path)
        invisible_folder = os.path.join(self.path, f".hub_{current_folder}")
        if not os.path.exists(invisible_folder):
            raise FileNotFoundError("[ERRO] Pasta de controle não encontrada")

        # Obtém os padrões do .gitignore
        gitignore_patterns = self.read_gitignore()

        # Lista de itens para ignorar durante a cópia
        default_ignore_patterns = [
            ".git",           # Pasta git
            ".hub_",          # Nossas pastas invisíveis
            "__pycache__",    # Cache Python
            "*.pyc",          # Arquivos compilados Python
            ".vscode",        # Configurações VS Code
        ]
        
        def should_ignore(name):
            full_path = os.path.join(self.path, name)
            
            # Verifica os padrões padrão
            for pattern in default_ignore_patterns:
                if pattern.startswith("*."):
                    if name.endswith(pattern[2:]):
                        return True
                elif pattern.startswith("*"):
                    if name.endswith(pattern[1:]):
                        return True
                elif name == pattern or name.startswith(pattern + os.sep):
                    return True
            
            # Verifica os padrões do .gitignore
            for pattern in gitignore_patterns:
                if pattern and not pattern.startswith('#'):
                    if self.matches_gitignore_pattern(full_path, pattern):
                        return True
            
            return False
        
        files_processed = {"added": [], "skipped": []}
        for item in os.listdir(self.path):
            if should_ignore(item):
                files_processed["skipped"].append(item)
                continue
            
            s = os.path.join(self.path, item)
            d = os.path.join(invisible_folder, item)
            
            try:
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                    files_processed["added"].append(f"{item}/")
                else:
                    shutil.copy2(s, d)
                    files_processed["added"].append(item)
            except PermissionError:
                print(yellow(f"[AVISO] Permissão negada: {item}"))

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