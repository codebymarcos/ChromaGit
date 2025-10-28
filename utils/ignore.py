# funcoes para processar arquivos .gitignore
import os
import shutil
import fnmatch
from pathlib import Path
from typing import List, Set, Optional

def find_gitignore(path: str) -> Optional[str]:
    # procura por arquivo .gitignore na pasta especificada
    gitignore_path = os.path.join(path, ".gitignore")
    if os.path.exists(gitignore_path):
        return gitignore_path
    return None

def read_gitignore_patterns(gitignore_path: str) -> List[str]:
    # le os padroes do arquivo .gitignore
    patterns = []
    try:
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # ignora linhas vazias e comentarios
                if line and not line.startswith('#'):
                    patterns.append(line)
    except Exception as e:
        pass
    return patterns

def should_ignore(path: str, patterns: List[str]) -> bool:
    # verifica se um arquivo/pasta deve ser ignorado baseado nos padroes
    path_obj = Path(path)
    
    for pattern in patterns:
        # converte padrao para formato do pathlib
        if pattern.startswith('/'):
            # padrao absoluto - remove a barra inicial
            pattern = pattern[1:]
        
        # verifica se o caminho corresponde ao padrao
        if fnmatch.fnmatch(str(path_obj), pattern) or fnmatch.fnmatch(path_obj.name, pattern):
            return True
        
        # verifica se algum parent corresponde ao padrao
        for parent in path_obj.parents:
            if fnmatch.fnmatch(str(parent), pattern) or fnmatch.fnmatch(parent.name, pattern):
                return True
    
    return False

def remove_ignored_files(source_path: str, dest_path: str, gitignore_path: str, additional_patterns: List[str] = None) -> bool:
    # funcao principal: copia pasta removendo arquivos listados no .gitignore
    try:
        # verifica se a pasta origem existe
        if not os.path.exists(source_path):
            return False
        
        # verifica se o .gitignore existe
        if not os.path.exists(gitignore_path):
            return False
        
        # le os padroes do .gitignore
        patterns = read_gitignore_patterns(gitignore_path)
        
        # adiciona padroes extras se fornecidos
        if additional_patterns:
            patterns.extend(additional_patterns)
        
        if not patterns:
            return False
        
        # cria a pasta destino se nao existir
        os.makedirs(dest_path, exist_ok=True)
        
        # percorre a arvore de arquivos
        for root, dirs, files in os.walk(source_path):
            # calcula o caminho relativo
            rel_root = os.path.relpath(root, source_path)
            if rel_root == '.':
                rel_root = ''
            
            # filtra diretorios que devem ser ignorados
            dirs_to_remove = []
            for d in dirs:
                dir_path = os.path.join(root, d)
                rel_dir_path = os.path.join(rel_root, d) if rel_root else d
                
                if should_ignore(rel_dir_path, patterns):
                    dirs_to_remove.append(d)
            
            # remove diretorios ignorados da lista para nao processar
            for d in dirs_to_remove:
                dirs.remove(d)
            
            # processa arquivos
            for file in files:
                file_path = os.path.join(root, file)
                rel_file_path = os.path.join(rel_root, file) if rel_root else file
                
                if not should_ignore(rel_file_path, patterns):
                    # copia o arquivo
                    dest_file_path = os.path.join(dest_path, rel_file_path)
                    dest_dir = os.path.dirname(dest_file_path)
                    
                    # cria diretorio destino se necessario
                    os.makedirs(dest_dir, exist_ok=True)
                    
                    # copia o arquivo
                    shutil.copy2(file_path, dest_file_path)
        
        return True
        
    except Exception as e:
        return False

def process_gitignore_folder(source_path: str, dest_path: str, ignore_patterns: List[str] = None) -> bool:
    # funcao principal que procura .gitignore e processa a pasta
    # procura o .gitignore na pasta origem
    gitignore_path = find_gitignore(source_path)
    if not gitignore_path:
        return False
    
    # processa a pasta removendo arquivos ignorados
    return remove_ignored_files(source_path, dest_path, gitignore_path, ignore_patterns)

