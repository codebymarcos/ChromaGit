import os
import sys
import json

__path__ = [os.path.dirname(os.path.abspath(__file__)), ".."]
sys.path.extend(__path__)

from models.cohe import generate
from core.cache import get_cache
from core.context import ContextManager

prompt_template = """Você é um assistente de programação preciso.

Tarefa: {intention}

Contexto do projeto:
{context}

Arquivos relevantes:
{files_content}

Dependências detectadas:
{dependencies}

Instruções:
1. Identifique exatamente onde editar (arquivo, linha, função/classe)
2. Descreva as alterações necessárias de forma concisa
3. Retorne apenas o essencial para implementar a tarefa

Resposta:"""

def tokenizer(text, api_key, project_root=None):
    cache = get_cache()
    
    # 1. resumir intenção (com cache)
    cache_key = f"intention:{text}"
    intention = cache.get(cache_key, max_age=3600)
    
    if not intention:
        sys_prompt = "Resuma em 1 frase clara e técnica a intenção do desenvolvedor."
        intention = generate(api_key, sys_prompt, f"Intenção: {text}").strip()
        cache.set(cache_key, intention)
    
    # 2. localizar estrutura_projeto.json
    if not project_root:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    json_path = os.path.join(project_root, 'estrutura_projeto.json')
    if not os.path.exists(json_path):
        return {"error": "estrutura_projeto.json não encontrado. Execute locate/dds.py primeiro."}
    
    with open(json_path, 'r', encoding='utf-8') as f:
        estrutura = json.load(f)
    
    # 3. analisar contexto profundo
    context_mgr = ContextManager(project_root)
    context_mgr.analyze_project()
    
    # 4. buscar arquivos relevantes usando LLM + contexto
    context_text = _build_context_summary(estrutura, context_mgr)
    
    cache_key_files = f"files:{intention}:{project_root}"
    relevantes = cache.get(cache_key_files, max_age=1800)
    
    if not relevantes:
        sys_prompt2 = "Liste apenas os nomes dos arquivos (separados por vírgula) mais relevantes para a tarefa."
        relevantes = generate(api_key, sys_prompt2, f"Tarefa: {intention}\n\nArquivos:\n{context_text}")
        cache.set(cache_key_files, relevantes)
    
    arquivos_alvo = [a.strip() for a in relevantes.split(',') if a.strip()]
    
    # 5. incluir arquivos relacionados por dependencias
    expanded_files = set(arquivos_alvo)
    for alvo in arquivos_alvo:
        related = context_mgr.get_related_files(alvo, depth=1)
        expanded_files.update(related[:3])  # limitar
    
    arquivos_alvo = list(expanded_files)[:5]  # max 5 arquivos
    
    # 6. ler código dos arquivos relevantes
    files_content = ""
    dependencies_info = ""
    
    for item in estrutura.get('estrutura', []):
        if any(alvo in item['caminho'] for alvo in arquivos_alvo):
            file_path = os.path.join(estrutura['path'], item['caminho'])
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # adicionar contexto de simbolos
                symbols = context_mgr.symbols.get(item['caminho'], [])
                symbol_summary = ", ".join([s['name'] for s in symbols[:10]])
                
                files_content += f"\n### {item['caminho']}\n"
                files_content += f"Símbolos: {symbol_summary}\n"
                files_content += f"```python\n{content}\n```\n"
                
                # info de dependencias
                deps = context_mgr.dependencies.get(item['caminho'], [])
                if deps:
                    dependencies_info += f"{item['caminho']} → {', '.join(list(deps)[:3])}\n"
    
    # 7. gerar análise de onde e o que editar (com cache parcial)
    sys_prompt3 = "Analise o código e indique: arquivo, linha/função, e mudança exata (máx 3 frases)."
    onde_editar = generate(api_key, sys_prompt3, 
                          f"Tarefa: {intention}\n\nCódigo:\n{files_content[:3000]}")
    
    # 8. montar prompt final
    final_prompt = prompt_template.format(
        intention=intention,
        context=context_text[:500],
        files_content=files_content[:2000],
        dependencies=dependencies_info[:300]
    )
    
    return {
        'intention': intention,
        'target_files': arquivos_alvo,
        'edit_plan': onde_editar,
        'final_prompt': final_prompt,
        'context': context_mgr.get_summary(),
        'cache_stats': cache.stats()
    }

def _build_context_summary(estrutura, context_mgr):
    # monta resumo compacto: arquivo -> funções/classes + complexidade
    lines = []
    for item in estrutura.get('estrutura', []):
        nome = item.get('caminho', item.get('nome', '?'))
        desc = item.get('descricao', '')[:80]
        funcoes = [f['nome'] for f in item.get('funcoes', [])]
        classes = [c['nome'] for c in item.get('classes', [])]
        
        parts = [nome, desc]
        if funcoes:
            parts.append(f"funcs: {', '.join(funcoes[:4])}")
        if classes:
            parts.append(f"classes: {', '.join(classes[:4])}")
        
        # adicionar complexidade se disponivel
        file_path = os.path.join(estrutura.get('path', ''), nome)
        if os.path.exists(file_path):
            complexity = context_mgr.get_file_complexity(file_path)
            parts.append(f"score: {complexity['score']}")
        
        lines.append(' | '.join(parts))
    
    return '\n'.join(lines[:30])