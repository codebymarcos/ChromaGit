# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.cohe import generate

class DocumentationGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def generate_docstrings(self, code):
        # gerar docstrings para funções/classes
        sys_prompt = """Você é um especialista em documentação Python. 
Gere docstrings estilo Google para todas funções e classes.
Retorne APENAS o código com docstrings adicionadas."""
        
        user_prompt = f"Adicione docstrings completas:\n\n```python\n{code}\n```"
        
        try:
            response = generate(self.api_key, sys_prompt, user_prompt)
            
            if '```python' in response:
                return response.split('```python')[1].split('```')[0].strip()
            elif '```' in response:
                return response.split('```')[1].strip()
            return response.strip()
        except:
            return code
    
    def generate_readme(self, project_root):
        # gerar README.md automático
        sys_prompt = "Você é um especialista em documentação de projetos. Crie um README.md profissional."
        
        # coletar info do projeto
        files = []
        for root, dirs, fs in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv']]
            for f in fs:
                if f.endswith('.py'):
                    files.append(os.path.relpath(os.path.join(root, f), project_root))
        
        user_prompt = f"""Crie um README.md para este projeto Python.

Estrutura do projeto:
{chr(10).join(files[:20])}

Inclua:
1. Título e descrição
2. Instalação
3. Uso básico
4. Estrutura do projeto
5. Contribuição
6. Licença

Retorne em formato Markdown."""
        
        try:
            return generate(self.api_key, sys_prompt, user_prompt).strip()
        except:
            return "# Projeto\n\nDocumentação em breve."
    
    def generate_inline_comments(self, code):
        # adicionar comentários explicativos
        sys_prompt = "Adicione comentários inline explicativos em código Python complexo."
        user_prompt = f"```python\n{code}\n```"
        
        try:
            response = generate(self.api_key, sys_prompt, user_prompt)
            
            if '```python' in response:
                return response.split('```python')[1].split('```')[0].strip()
            elif '```' in response:
                return response.split('```')[1].strip()
            return response.strip()
        except:
            return code
    
    def generate_api_docs(self, code):
        # gerar documentação de API
        sys_prompt = "Gere documentação de API em Markdown para este código Python."
        user_prompt = f"```python\n{code}\n```"
        
        try:
            return generate(self.api_key, sys_prompt, user_prompt).strip()
        except:
            return "# API Documentation\n\nEm breve."
    
    def explain_code(self, code, level='beginner'):
        # explicar código para diferentes níveis
        levels = {
            'beginner': 'Explique de forma simples para iniciantes',
            'intermediate': 'Explique de forma técnica',
            'expert': 'Análise profunda e padrões avançados'
        }
        
        sys_prompt = f"{levels.get(level, levels['beginner'])} este código Python."
        user_prompt = f"```python\n{code}\n```"
        
        try:
            return generate(self.api_key, sys_prompt, user_prompt).strip()
        except:
            return "Erro ao gerar explicação."
