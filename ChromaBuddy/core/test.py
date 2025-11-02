

import os
import sys
import subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.cohe import generate
from core.execute import execute

def test(execute_result, tokenizer_result, api_key, project_root, max_attempts=3):
    # validar entrada
    if execute_result.get('modified', 0) == 0:
        return {'status': 'nada para testar', 'message': 'Nenhum arquivo foi modificado'}
    
    results = []
    
    # testar cada arquivo modificado
    for change in execute_result['changes']:
        if change['status'] != 'modificado':
            continue
        
        file_path = _find_file(project_root, change['file'])
        if not file_path:
            results.append({'file': change['file'], 'status': 'não encontrado'})
            continue
        
        # tentar executar até max_attempts vezes
        for attempt in range(1, max_attempts + 1):
            test_result = _run_file(file_path)
            
            if test_result['success']:
                # sucesso!
                msg = _generate_success_message(change['file'], api_key)
                results.append({
                    'file': change['file'],
                    'status': 'sucesso',
                    'attempts': attempt,
                    'message': msg
                })
                break
            else:
                # erro encontrado
                if attempt < max_attempts:
                    # tentar corrigir
                    fix_result = _auto_fix(file_path, test_result['error'], 
                                          tokenizer_result['intention'], api_key)
                    
                    if not fix_result:
                        results.append({
                            'file': change['file'],
                            'status': 'erro',
                            'attempts': attempt,
                            'error': test_result['error']
                        })
                        break
                else:
                    # max tentativas atingido
                    results.append({
                        'file': change['file'],
                        'status': 'erro',
                        'attempts': attempt,
                        'error': test_result['error']
                    })
    
    # resumo final
    success = sum(1 for r in results if r['status'] == 'sucesso')
    return {'total': len(results), 'success': success, 'results': results}

def _find_file(project_root, target):
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv']]
        for f in files:
            if target in f or f == target:
                return os.path.join(root, f)
    return None

def _run_file(file_path):
    # executar arquivo Python e capturar saída
    try:
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            return {'success': True, 'output': result.stdout}
        else:
            return {'success': False, 'error': result.stderr or result.stdout}
    
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Timeout: execução demorou mais de 10s'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def _auto_fix(file_path, error, intention, api_key):
    # ler código atual com erro
    with open(file_path, 'r', encoding='utf-8') as f:
        broken_code = f.read()
    
    # gerar correção com LLM
    sys_prompt = "Você é um debugger Python expert. Corrija o código abaixo para resolver o erro."
    user_prompt = f"""CÓDIGO ATUAL:
```python
{broken_code}
```

ERRO:
{error[:500]}

INTENÇÃO ORIGINAL: {intention}

Retorne o código completo corrigido em ```python ... ```"""
    
    try:
        response = generate(api_key, sys_prompt, user_prompt).strip()
        
        # extrair código corrigido
        if '```python' in response:
            parts = response.split('```python', 1)
            if len(parts) > 1:
                fixed_code = parts[1].split('```')[0].strip()
            else:
                return False
        elif '```' in response:
            parts = response.split('```', 2)
            if len(parts) >= 2:
                fixed_code = parts[1].strip()
            else:
                return False
        else:
            fixed_code = response.strip()
        
        # salvar código corrigido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_code)
        
        return True
    
    except Exception as e:
        return False

def _generate_success_message(filename, api_key):
    # gerar mensagem de sucesso personalizada
    sys_prompt = "Gere uma mensagem curta (1 frase) celebrando o sucesso da modificação do código."
    user_prompt = f"Arquivo '{filename}' foi modificado e testado com sucesso!"
    
    try:
        return generate(api_key, sys_prompt, user_prompt).strip()
    except:
        return f"✓ {filename} modificado e testado com sucesso!"