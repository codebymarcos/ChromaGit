# -*- coding: utf-8 -*-
import os
import ast
import json
from collections import defaultdict

class ContextManager:
    def __init__(self, project_root):
        self.project_root = project_root
        self.symbols = defaultdict(list)
        self.imports = defaultdict(set)
        self.call_graph = defaultdict(set)
        self.dependencies = defaultdict(set)
    
    def analyze_project(self):
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    self._analyze_file(filepath)
        
        self._build_dependency_graph()
        return self.get_summary()
    
    def _analyze_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=filepath)
            rel_path = os.path.relpath(filepath, self.project_root)
            
            # extrair simbolos
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.symbols[rel_path].append({
                        'type': 'function',
                        'name': node.name,
                        'line': node.lineno,
                        'args': [a.arg for a in node.args.args]
                    })
                
                elif isinstance(node, ast.ClassDef):
                    self.symbols[rel_path].append({
                        'type': 'class',
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports[rel_path].add(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.imports[rel_path].add(node.module)
                
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        self.call_graph[rel_path].add(node.func.id)
        
        except:
            pass
    
    def _build_dependency_graph(self):
        for file, imports in self.imports.items():
            for imp in imports:
                # tentar mapear para arquivo local
                for other_file in self.symbols.keys():
                    module = other_file.replace('.py', '').replace(os.sep, '.')
                    if imp.endswith(module) or module.endswith(imp):
                        self.dependencies[file].add(other_file)
    
    def get_related_files(self, filepath, depth=2):
        related = set()
        queue = [(filepath, 0)]
        visited = set()
        
        while queue:
            current, d = queue.pop(0)
            if current in visited or d > depth:
                continue
            
            visited.add(current)
            related.add(current)
            
            # arquivos que current importa
            for dep in self.dependencies.get(current, []):
                if dep not in visited:
                    queue.append((dep, d + 1))
            
            # arquivos que importam current
            for file, deps in self.dependencies.items():
                if current in deps and file not in visited:
                    queue.append((file, d + 1))
        
        return list(related)
    
    def find_symbol(self, name):
        results = []
        for file, syms in self.symbols.items():
            for sym in syms:
                if sym['name'] == name:
                    results.append({'file': file, **sym})
        return results
    
    def get_file_complexity(self, filepath):
        rel_path = os.path.relpath(filepath, self.project_root)
        symbols = self.symbols.get(rel_path, [])
        imports = len(self.imports.get(rel_path, []))
        deps = len(self.dependencies.get(rel_path, []))
        
        return {
            'symbols': len(symbols),
            'imports': imports,
            'dependencies': deps,
            'score': len(symbols) * 2 + imports + deps * 3
        }
    
    def get_summary(self):
        return {
            'total_files': len(self.symbols),
            'total_symbols': sum(len(s) for s in self.symbols.values()),
            'total_imports': sum(len(i) for i in self.imports.values()),
            'files': list(self.symbols.keys())
        }
