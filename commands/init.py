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
        """
        Lê e processa os padrões do arquivo .gitignore.
        Suporta:
        - Comentários (#)
        - Negação de padrões (!)
        - Diretórios específicos (/)
        - Wildcards (*, **, ?, [abc], [0-9])
        """
        gitignore_path = os.path.join(self.path, '.gitignore')
        patterns = []
        if not os.path.exists(gitignore_path):
            return patterns

        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Pula linhas vazias e comentários
                if not line or line.startswith('#'):
                    continue
                
                # Processa padrões de negação
                is_negative = line.startswith('!')
                if is_negative:
                    line = line[1:].strip()
                
                # Remove barras duplicadas e barras do final
                line = line.replace('//', '/')
                line = line.rstrip('/')
                
                # Converte padrões para formato glob
                if line.startswith('/'):
                    line = line[1:]  # Remove barra inicial para padrões absolutos
                elif not line.startswith('*'):
                    line = f"**/{line}"  # Torna padrão relativo recursivo
                
                patterns.append({
                    'pattern': line,
                    'is_negative': is_negative,
                    'is_dir': line.endswith('/'),
                    'is_recursive': '**' in line
                })
                
        return patterns

    def matches_gitignore_pattern(self, filepath, pattern_info):
        """
        Verifica se um arquivo corresponde a um padrão do .gitignore
        
        Args:
            filepath: Caminho do arquivo a verificar
            pattern_info: Dicionário com informações do padrão:
                - pattern: O padrão em si
                - is_negative: Se é um padrão de negação
                - is_dir: Se é específico para diretório
                - is_recursive: Se usa matching recursivo (**)
        """
        import fnmatch, re
        from pathlib import Path

        path = Path(filepath)
        try:
            relative_path = path.relative_to(Path(self.path))
        except ValueError:
            return False

        # Se o padrão é específico para diretório e o arquivo não é um diretório
        if pattern_info['is_dir'] and not os.path.isdir(filepath):
            return False

        pattern = pattern_info['pattern']
        path_str = str(relative_path).replace('\\', '/')
        
        # Trata padrões com /**/ para matching em qualquer nível
        if '/**/' in pattern:
            parts = pattern.split('/**/')
            return self._matches_parts(path_str, parts)
            
        # Trata padrões com ** para matching recursivo
        elif pattern.startswith('**/'):
            return fnmatch.fnmatch(path_str, pattern[3:]) or fnmatch.fnmatch(path_str, pattern)
            
        # Trata padrões absolutos (sem ** no início)
        elif not pattern.startswith('*'):
            return fnmatch.fnmatch(path_str, pattern)
            
        # Padrão normal
        return fnmatch.fnmatch(path_str, pattern)
    
    def _matches_parts(self, path, pattern_parts):
        """Auxiliar para verificar padrões com /**/ (matching em qualquer nível)"""
        if not pattern_parts:
            return True
        
        current = pattern_parts[0]
        remaining = pattern_parts[1:]
        
        path_parts = path.split('/')
        for i in range(len(path_parts)):
            subpath = '/'.join(path_parts[i:])
            if fnmatch.fnmatch(subpath, current):
                if not remaining:
                    return True
                if self._matches_parts(subpath, remaining):
                    return True
        return False

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
            
            # Primeiro verifica padrões negativos do .gitignore
            matched_negative = False
            for pattern in gitignore_patterns:
                if pattern['is_negative'] and self.matches_gitignore_pattern(full_path, pattern):
                    matched_negative = True
                    break
                    
            # Se tiver match com padrão negativo, não ignora
            if matched_negative:
                return False
                
            # Depois verifica padrões normais do .gitignore
            for pattern in gitignore_patterns:
                if not pattern['is_negative'] and self.matches_gitignore_pattern(full_path, pattern):
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