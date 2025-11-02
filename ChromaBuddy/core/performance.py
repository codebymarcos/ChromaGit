# -*- coding: utf-8 -*-
import time
import cProfile
import pstats
import io
from functools import wraps

class PerformanceOptimizer:
    def __init__(self):
        self.profiles = {}
        self.timings = {}
    
    def profile_function(self, func):
        # decorator para profile
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()
            
            result = func(*args, **kwargs)
            
            profiler.disable()
            
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(10)
            
            self.profiles[func.__name__] = s.getvalue()
            
            return result
        
        return wrapper
    
    def time_function(self, func):
        # decorator para timing
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            
            if func.__name__ not in self.timings:
                self.timings[func.__name__] = []
            
            self.timings[func.__name__].append(elapsed)
            
            return result
        
        return wrapper
    
    def analyze_bottlenecks(self, code):
        # analisar gargalos no código
        import ast
        
        issues = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # loops aninhados
                if isinstance(node, ast.For):
                    for child in ast.walk(node):
                        if isinstance(child, ast.For) and child != node:
                            issues.append({
                                'type': 'nested_loop',
                                'line': node.lineno,
                                'severity': 'high',
                                'suggestion': 'Considere usar list comprehension ou vetorização'
                            })
                
                # múltiplas chamadas de função em loop
                if isinstance(node, ast.For):
                    calls = [n for n in ast.walk(node.body[0]) if isinstance(n, ast.Call)]
                    if len(calls) > 3:
                        issues.append({
                            'type': 'many_calls_in_loop',
                            'line': node.lineno,
                            'severity': 'medium',
                            'suggestion': 'Cache resultados de funções fora do loop'
                        })
        
        except:
            pass
        
        return issues
    
    def suggest_optimizations(self, code):
        # sugestões de otimização
        suggestions = []
        
        # verificar uso de + para strings
        if '"+' in code or "+ \"" in code:
            suggestions.append({
                'issue': 'String concatenation com +',
                'fix': 'Use f-strings ou join() para melhor performance'
            })
        
        # verificar loops desnecessários
        if 'for ' in code and 'append(' in code:
            suggestions.append({
                'issue': 'Loop com append',
                'fix': 'Considere usar list comprehension'
            })
        
        # verificar global lookups
        if re.findall(r'\b(len|range|str|int)\s*\(', code):
            suggestions.append({
                'issue': 'Lookups globais em loops',
                'fix': 'Armazene funções builtin em variáveis locais dentro de loops'
            })
        
        return suggestions
    
    def get_stats(self):
        # estatísticas de performance
        stats = {'profiles': len(self.profiles), 'timings': {}}
        
        for func, times in self.timings.items():
            stats['timings'][func] = {
                'count': len(times),
                'avg': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
                'total': sum(times)
            }
        
        return stats

import re
