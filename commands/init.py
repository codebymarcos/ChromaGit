import os
import shutil

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
            raise FileNotFoundError("A pasta invisivel nao existe.")

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
                    if name.endswith(pattern[2:]):  # Removemos o *. do padrão
                        return True
                elif pattern.startswith("*"):
                    if name.endswith(pattern[1:]):  # Remove só o *
                        return True
                elif name == pattern or name.startswith(pattern + os.sep):
                    return True
            
            # Verifica os padrões do .gitignore
            for pattern in gitignore_patterns:
                if pattern and not pattern.startswith('#'):
                    if self.matches_gitignore_pattern(full_path, pattern):
                        print(f"Ignorando {name} devido ao padrão {pattern}")  # Debug
                        return True
            
            return False
        
        for item in os.listdir(self.path):
            if should_ignore(item):
                continue
            
            s = os.path.join(self.path, item)
            d = os.path.join(invisible_folder, item)
            
            try:
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            except PermissionError:
                print(f"Aviso: Sem permissão para copiar {item}, ignorando...")

# testar a classe
if __name__ == "__main__":
    def print_separator():
        print("\n" + "="*50 + "\n")

    print("Iniciando testes do comando init...")
    print_separator()
    
    # Inicializa a classe com o diretório atual
    init = Init(os.getcwd())
    print("Diretório atual:", init.path)
    
    print_separator()
    print("1. Testando criação da pasta invisível...")
    invisible_folder = init.create_invisible_folder()
    print("✓ Pasta invisível criada em:", invisible_folder)
    
    print_separator()
    print("2. Verificando existência da pasta invisível...")
    exists = init.check_invisible_folder()
    print("✓ Status da pasta invisível:", "Existe" if exists else "Não existe")
    
    print_separator()
    print("3. Lendo padrões do .gitignore...")
    gitignore_patterns = init.read_gitignore()
    print("✓ Padrões encontrados no .gitignore:")
    for pattern in gitignore_patterns:
        print(f"  - {pattern}")
    
    print_separator()
    print("4. Copiando arquivos para a pasta invisível...")
    try:
        init.copy_files_to_invisible_folder()
        print("✓ Arquivos copiados com sucesso!")
    except Exception as e:
        print("✗ Erro ao copiar arquivos:", str(e))
    
    print_separator()
    print("Testes concluídos!")