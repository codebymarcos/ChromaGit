# -*- coding: utf-8 -*-
import ast
import re

class CodeAnalyzer:
    def __init__(self):
        self.issues = []
    
    def analyze(self, code, filepath=""):
        self.issues = []
        
        try:
            tree = ast.parse(code)
            
            # 1. complexidade ciclomatica
            complexity = self._check_complexity(tree)
            
            # 2. funções muito longas
            long_funcs = self._check_function_length(tree, code)
            
            # 3. variaveis nao usadas
            unused = self._check_unused_vars(tree)
            
            # 4. imports duplicados
            dup_imports = self._check_duplicate_imports(tree)
            
            # 5. magic numbers
            magic = self._check_magic_numbers(tree, code)
            
            # 6. naming conventions
            naming = self._check_naming(tree)
            
            # 7. docstrings faltando
            missing_docs = self._check_docstrings(tree)
            
            # 8. código duplicado
            duplicates = self._check_duplicates(code)
            
            return {
                'filepath': filepath,
                'complexity': complexity,
                'long_functions': long_funcs,
                'unused_vars': unused,
                'duplicate_imports': dup_imports,
                'magic_numbers': magic,
                'naming_issues': naming,
                'missing_docstrings': missing_docs,
                'duplicates': duplicates,
                'score': self._calculate_score(),
                'issues': self.issues
            }
        
        except SyntaxError as e:
            return {'error': str(e), 'issues': []}
    
    def _check_complexity(self, tree):
        complex_funcs = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                cyclo = self._cyclomatic_complexity(node)
                if cyclo > 10:
                    complex_funcs.append({'name': node.name, 'complexity': cyclo, 'line': node.lineno})
                    self.issues.append(f"Linha {node.lineno}: função '{node.name}' muito complexa ({cyclo})")
        return complex_funcs
    
    def _cyclomatic_complexity(self, node):
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def _check_function_length(self, tree, code):
        long_funcs = []
        lines = code.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                end_line = node.end_lineno or node.lineno
                length = end_line - node.lineno
                
                if length > 50:
                    long_funcs.append({'name': node.name, 'lines': length, 'line': node.lineno})
                    self.issues.append(f"Linha {node.lineno}: função '{node.name}' muito longa ({length} linhas)")
        
        return long_funcs
    
    def _check_unused_vars(self, tree):
        unused = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                assigned = set()
                used = set()
                
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        if isinstance(child.ctx, ast.Store):
                            assigned.add(child.id)
                        elif isinstance(child.ctx, ast.Load):
                            used.add(child.id)
                
                for var in assigned - used:
                    if not var.startswith('_'):
                        unused.append({'var': var, 'function': node.name, 'line': node.lineno})
        
        return unused
    
    def _check_duplicate_imports(self, tree):
        imports = []
        seen = set()
        duplicates = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in seen:
                        duplicates.append({'module': alias.name, 'line': node.lineno})
                    seen.add(alias.name)
        
        return duplicates
    
    def _check_magic_numbers(self, tree, code):
        magic = []
        for node in ast.walk(tree):
            # Python 3.14+ usa ast.Constant ao invés de ast.Num
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in [0, 1, -1, 2] and hasattr(node, 'lineno'):
                    magic.append({'value': node.value, 'line': node.lineno})
        return magic[:10]  # limitar
    
    def _check_naming(self, tree):
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    issues.append({'type': 'function', 'name': node.name, 'line': node.lineno})
            
            elif isinstance(node, ast.ClassDef):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    issues.append({'type': 'class', 'name': node.name, 'line': node.lineno})
        
        return issues
    
    def _check_docstrings(self, tree):
        missing = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    missing.append({'type': type(node).__name__, 'name': node.name, 'line': node.lineno})
        
        return missing[:15]  # limitar
    
    def _check_duplicates(self, code):
        lines = code.split('\n')
        duplicates = []
        seen = {}
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if len(stripped) > 20 and not stripped.startswith('#'):
                if stripped in seen:
                    duplicates.append({'line': i, 'duplicate_of': seen[stripped]})
                else:
                    seen[stripped] = i
        
        return duplicates[:10]
    
    def _calculate_score(self):
        penalty = len(self.issues) * 5
        return max(0, 100 - penalty)
    
    def suggest_improvements(self, analysis):
        suggestions = []
        
        if analysis.get('complexity'):
            suggestions.append("Refatorar funções complexas em funções menores")
        
        if analysis.get('long_functions'):
            suggestions.append("Dividir funções longas (>50 linhas)")
        
        if analysis.get('missing_docstrings'):
            suggestions.append("Adicionar docstrings às funções públicas")
        
        if analysis.get('magic_numbers'):
            suggestions.append("Substituir números mágicos por constantes nomeadas")
        
        if analysis.get('duplicates'):
            suggestions.append("Extrair código duplicado para funções reutilizáveis")
        
        return suggestions
