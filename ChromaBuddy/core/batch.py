# -*- coding: utf-8 -*-
import os
import ast
import re

class BatchOperations:
    def __init__(self, project_root):
        self.project_root = project_root
        self.operations = []
    
    def rename_symbol(self, old_name, new_name, symbol_type='all'):
        # renomear função/classe em todos os arquivos
        files_modified = []
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        modified = False
                        new_content = content
                        
                        # renomear definições
                        if symbol_type in ['all', 'class']:
                            new_content, n = re.subn(
                                f"class {old_name}\\b",
                                f"class {new_name}",
                                new_content
                            )
                            modified = modified or n > 0
                        
                        if symbol_type in ['all', 'function']:
                            new_content, n = re.subn(
                                f"def {old_name}\\b",
                                f"def {new_name}",
                                new_content
                            )
                            modified = modified or n > 0
                        
                        # renomear usos
                        new_content, n = re.subn(
                            f"\\b{old_name}\\b",
                            new_name,
                            new_content
                        )
                        modified = modified or n > 0
                        
                        if modified:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            files_modified.append(filepath)
                    
                    except:
                        pass
        
        return {
            'old_name': old_name,
            'new_name': new_name,
            'files_modified': files_modified,
            'count': len(files_modified)
        }
    
    def extract_function(self, filepath, start_line, end_line, new_func_name):
        # extrair código para nova função
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # extrair linhas
        extracted = lines[start_line-1:end_line]
        
        # detectar indentação
        indent = len(extracted[0]) - len(extracted[0].lstrip())
        
        # criar nova função
        new_func = f"def {new_func_name}():\n"
        for line in extracted:
            new_func += "    " + line[indent:]
        
        # substituir por chamada
        call_indent = " " * indent
        lines[start_line-1:end_line] = [f"{call_indent}{new_func_name}()\n"]
        
        # inserir função antes
        lines.insert(start_line-1, "\n" + new_func + "\n")
        
        # salvar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return {'function': new_func_name, 'file': filepath}
    
    def add_import_to_all(self, import_statement):
        # adicionar import em todos os arquivos Python
        files_modified = []
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if import_statement not in content:
                            # inserir após outros imports
                            lines = content.split('\n')
                            insert_pos = 0
                            
                            for i, line in enumerate(lines):
                                if line.startswith('import ') or line.startswith('from '):
                                    insert_pos = i + 1
                            
                            lines.insert(insert_pos, import_statement)
                            
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write('\n'.join(lines))
                            
                            files_modified.append(filepath)
                    except:
                        pass
        
        return {'import': import_statement, 'files': files_modified, 'count': len(files_modified)}
    
    def remove_unused_imports(self):
        # remover imports não usados em todos arquivos
        files_modified = []
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    
                    if self._remove_unused_in_file(filepath):
                        files_modified.append(filepath)
        
        return {'files': files_modified, 'count': len(files_modified)}
    
    def _remove_unused_in_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            imported = set()
            used = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported.add(node.module.split('.')[0])
                elif isinstance(node, ast.Name):
                    used.add(node.id)
            
            unused = imported - used
            
            if unused:
                lines = content.split('\n')
                new_lines = []
                
                for line in lines:
                    skip = False
                    for imp in unused:
                        if f"import {imp}" in line or f"from {imp}" in line:
                            skip = True
                            break
                    
                    if not skip:
                        new_lines.append(line)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                
                return True
        
        except:
            pass
        
        return False
    
    def format_all_files(self):
        # formatar todos arquivos (remover linhas vazias extras, etc)
        files_formatted = []
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        
                        # remover linhas vazias consecutivas (max 2)
                        formatted = []
                        empty_count = 0
                        
                        for line in lines:
                            if line.strip() == '':
                                empty_count += 1
                                if empty_count <= 2:
                                    formatted.append(line)
                            else:
                                empty_count = 0
                                formatted.append(line)
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.writelines(formatted)
                        
                        files_formatted.append(filepath)
                    
                    except:
                        pass
        
        return {'files': files_formatted, 'count': len(files_formatted)}
