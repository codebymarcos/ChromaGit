# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.cohe import generate

class TestGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def generate_unit_tests(self, code, filepath=""):
        sys_prompt = """Você é um especialista em testes Python. Gere testes unitários completos usando pytest.
        
REGRAS:
- Use pytest e fixtures quando apropriado
- Teste casos normais, edge cases e erros
- Use mocks para dependências externas
- Gere testes parametrizados quando possível
- Inclua asserts claros e descritivos"""
        
        user_prompt = f"""Gere testes unitários completos para este código:

```python
{code}
```

Retorne apenas o código dos testes em ```python ... ```"""
        
        try:
            response = generate(self.api_key, sys_prompt, user_prompt)
            
            # extrair codigo
            if '```python' in response:
                test_code = response.split('```python')[1].split('```')[0].strip()
            elif '```' in response:
                test_code = response.split('```')[1].strip()
            else:
                test_code = response.strip()
            
            return test_code
        
        except Exception as e:
            return f"# Erro ao gerar testes: {e}"
    
    def generate_integration_tests(self, files_context):
        sys_prompt = "Gere testes de integração que testam a interação entre múltiplos módulos."
        
        user_prompt = f"""Contexto dos arquivos:
{files_context}

Gere testes de integração em ```python ... ```"""
        
        try:
            response = generate(self.api_key, sys_prompt, user_prompt)
            
            if '```python' in response:
                return response.split('```python')[1].split('```')[0].strip()
            elif '```' in response:
                return response.split('```')[1].strip()
            return response.strip()
        
        except Exception as e:
            return f"# Erro: {e}"
    
    def suggest_test_scenarios(self, code):
        sys_prompt = "Liste cenários de teste importantes (5-10 cenários curtos)"
        user_prompt = f"Código:\n```python\n{code[:1000]}\n```"
        
        try:
            scenarios = generate(self.api_key, sys_prompt, user_prompt)
            return scenarios.strip().split('\n')
        except:
            return []
    
    def generate_mock_data(self, function_signature):
        sys_prompt = "Gere dados de teste realistas para esta assinatura de função"
        user_prompt = function_signature
        
        try:
            return generate(self.api_key, sys_prompt, user_prompt).strip()
        except:
            return "{}"
