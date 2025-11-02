# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path

class MentionSystem:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.cache = {}
    
    def parse_mentions(self, text):
        # detecta @arquivo, @Classe, @funcao, @Classe.metodo
        mentions = {
            'files': [],
            'symbols': [],
            'methods': [],
            'raw': []
        }
        
        # padroes: @arquivo.py, @Classe, @funcao, @Classe.metodo
        patterns = [
            (r'@([\w/\\.-]+\.py)', 'file'),
            (r'@([A-Z]\w+)\.(\w+)', 'method'),
            (r'@([A-Z]\w+)', 'class'),
            (r'@([a-z_]\w+)', 'function')
        ]
        
        for pattern, tipo in patterns:
            for match in re.finditer(pattern, text):
                mention = match.group(0)
                mentions['raw'].append(mention)
                
                if tipo == 'file':
                    filepath = match.group(1)
                    mentions['files'].append(filepath)
                elif tipo == 'method':
                    class_name = match.group(1)
                    method_name = match.group(2)
                    mentions['methods'].append(f"{class_name}.{method_name}")
                    mentions['symbols'].append(class_name)
                elif tipo in ['class', 'function']:
                    mentions['symbols'].append(match.group(1))
        
        return mentions
    
    def resolve_mentions(self, mentions):
        # resolve menções para conteúdo real
        resolved = {
            'files': {},
            'symbols': {},
            'context': ""
        }
        
        # resolver arquivos
        for file_ref in mentions['files']:
            content = self._find_and_read_file(file_ref)
            if content:
                resolved['files'][file_ref] = content
        
        # resolver símbolos (classes, funções)
        for symbol in mentions['symbols']:
            locations = self._find_symbol(symbol)
            if locations:
                resolved['symbols'][symbol] = locations
        
        # montar contexto formatado
        context = self._build_context(resolved)
        resolved['context'] = context
        
        return resolved
    
    def _find_and_read_file(self, file_ref):
        # buscar arquivo no projeto
        possible_paths = [
            self.project_root / file_ref,
            self.project_root / 'core' / file_ref,
            self.project_root / 'teste' / file_ref
        ]
        
        # busca recursiva
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv']]
            for f in files:
                if f == file_ref or file_ref in f:
                    possible_paths.append(Path(root) / f)
        
        for path in possible_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return f.read()
                except:
                    pass
        
        return None
    
    def _find_symbol(self, symbol):
        # busca símbolo em todos arquivos Python
        locations = []
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = Path(root) / file
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # buscar definições
                        patterns = [
                            f"class {symbol}",
                            f"def {symbol}",
                        ]
                        
                        for pattern in patterns:
                            if pattern in content:
                                # extrair contexto ao redor
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    if pattern in line:
                                        start = max(0, i - 2)
                                        end = min(len(lines), i + 20)
                                        context = '\n'.join(lines[start:end])
                                        
                                        locations.append({
                                            'file': str(filepath.relative_to(self.project_root)),
                                            'line': i + 1,
                                            'context': context
                                        })
                    except:
                        pass
        
        return locations
    
    def _build_context(self, resolved):
        context = ""
        
        # adicionar arquivos mencionados
        if resolved['files']:
            context += "=== ARQUIVOS MENCIONADOS ===\n\n"
            for file_ref, content in resolved['files'].items():
                context += f"### @{file_ref}\n```python\n{content}\n```\n\n"
        
        # adicionar símbolos mencionados
        if resolved['symbols']:
            context += "=== SÍMBOLOS MENCIONADOS ===\n\n"
            for symbol, locations in resolved['symbols'].items():
                context += f"### @{symbol}\n"
                for loc in locations:
                    context += f"Arquivo: {loc['file']} (linha {loc['line']})\n"
                    context += f"```python\n{loc['context']}\n```\n\n"
        
        return context
    
    def suggest_completions(self, partial):
        # autocomplete para @
        if not partial.startswith('@'):
            return []
        
        query = partial[1:].lower()
        suggestions = []
        
        # sugerir arquivos
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv']]
            
            for file in files:
                if file.endswith('.py') and query in file.lower():
                    rel_path = os.path.relpath(os.path.join(root, file), self.project_root)
                    suggestions.append({
                        'type': 'file',
                        'text': f"@{rel_path}",
                        'description': f"Arquivo: {rel_path}"
                    })
        
        return suggestions[:10]
    
    def expand_prompt(self, prompt):
        # expandir prompt com contexto de menções
        mentions = self.parse_mentions(prompt)
        
        if not mentions['raw']:
            return prompt, None
        
        resolved = self.resolve_mentions(mentions)
        
        # criar prompt expandido
        expanded = f"{resolved['context']}\n\n{'='*60}\n\nSOLICITAÇÃO DO USUÁRIO:\n{prompt}"
        
        return expanded, {
            'mentions': mentions,
            'resolved': resolved,
            'files_count': len(resolved['files']),
            'symbols_count': len(resolved['symbols'])
        }
