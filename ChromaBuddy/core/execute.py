import os
import sys
import ast
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.cohe import generate
from core.diff import DiffManager
from core.analyzer import CodeAnalyzer
from core.cache import get_cache

programing_template = """Você é um editor de código Python especialista.

ARQUIVO COMPLETO: {filepath}
```python
{full_code}
```

ANÁLISE DE QUALIDADE:
{analysis}

TAREFA: {task}

INSTRUÇÕES:
1. Analise o arquivo completo acima
2. Considere a análise de qualidade para melhorar o código
3. Faça as modificações necessárias (adicionar, editar ou remover código)
4. Retorne o arquivo COMPLETO modificado
5. Mantenha toda formatação, imports e estrutura existente
6. PRESERVE comentários e docstrings importantes
7. NÃO adicione explicações, apenas retorne o código Python completo

ARQUIVO MODIFICADO COMPLETO:
```python"""

def execute(tokenizer_result, api_key, project_root):
    # validar entrada do tokenizer
    if 'error' in tokenizer_result or not tokenizer_result.get('target_files'):
        return {'error': 'Nenhum arquivo alvo encontrado', 'changes': []}
    
    changes = []
    diff_mgr = DiffManager()
    cache = get_cache()
    analyzer = CodeAnalyzer()
    
    # processar cada arquivo alvo
    for target_file in tokenizer_result['target_files']:
        file_path = _find_file(project_root, target_file)
        if not file_path:
            changes.append({'file': target_file, 'status': 'não encontrado'})
            continue
        
        # ler código completo atual
        with open(file_path, 'r', encoding='utf-8') as f:
            current_code = f.read()
        
        # salvar snapshot para rollback
        diff_mgr.save_snapshot(file_path, current_code)
        
        # analisar qualidade do código
        analysis = analyzer.analyze(current_code, file_path)
        analysis_summary = f"Score: {analysis.get('score', 0)}/100\n"
        analysis_summary += f"Issues: {len(analysis.get('issues', []))}\n"
        
        if analysis.get('complexity'):
            analysis_summary += f"Funções complexas: {len(analysis['complexity'])}\n"
        
        suggestions = analyzer.suggest_improvements(analysis)
        if suggestions:
            analysis_summary += f"Sugestões: {', '.join(suggestions[:3])}"
        
        # tentar usar cache
        cache_key = f"rewrite:{file_path}:{tokenizer_result['intention']}"
        modified_code = cache.get(cache_key, max_age=600)
        
        if not modified_code:
            # gerar código modificado (arquivo completo)
            modified_code = _rewrite_file(
                file_path, current_code, 
                tokenizer_result['intention'], 
                tokenizer_result['edit_plan'],
                analysis_summary,
                api_key
            )
            
            if modified_code:
                cache.set(cache_key, modified_code, ttl=600)
        
        if modified_code and modified_code != current_code:
            # gerar diff
            diff_result = diff_mgr.compare(current_code, modified_code, target_file)
            
            # aprovar interativamente
            approved = diff_mgr.interactive_approve(diff_result)
            
            if approved:
                # salvar arquivo modificado
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_code)
                
                # calcular resumo de mudanças
                summary = f"{diff_result['stats']['new_lines']} linhas ({diff_result['stats']['delta']:+d})"
                
                changes.append({
                    'file': target_file,
                    'status': 'modificado',
                    'details': summary,
                    'diff': diff_result
                })
            else:
                changes.append({'file': target_file, 'status': 'rejeitado'})
        else:
            changes.append({'file': target_file, 'status': 'sem mudanças'})
    
    # resumo final
    modified = sum(1 for c in changes if c['status'] == 'modificado')
    return {
        'total': len(changes),
        'modified': modified,
        'changes': changes,
        'cache_stats': cache.stats()
    }

def _find_file(project_root, target):
    # buscar arquivo recursivamente
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv']]
        for f in files:
            if target in f or f == target:
                return os.path.join(root, f)
    return None

def _rewrite_file(filepath, current_code, intention, plan, analysis, api_key):
    # gerar versão completa modificada do arquivo
    prompt = programing_template.format(
        filepath=os.path.basename(filepath),
        full_code=current_code,
        analysis=analysis,
        task=f"{intention}\n\nDetalhes: {plan}"
    )
    
    sys_prompt = "Você é um programador Python expert. Reescreva arquivos com precisão mantendo toda estrutura e lógica necessária."
    
    try:
        response = generate(api_key, sys_prompt, prompt).strip()
        
        # extrair código da resposta (remover markdown se presente)
        if '```python' in response:
            parts = response.split('```python', 1)
            if len(parts) > 1:
                code = parts[1].split('```')[0]
                return code.strip()
        elif '```' in response:
            parts = response.split('```', 2)
            if len(parts) >= 2:
                return parts[1].strip()
        
        # se não tem markdown, assumir que é código direto
        return response.strip()
    
    except Exception as e:
        print(f"Erro ao gerar código: {e}")
        return None
