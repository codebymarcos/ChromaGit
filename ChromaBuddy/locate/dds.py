
import os
import json
import ast
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.cohe import generate

def cltdds(path, api_key):
    """
    Coleta informações sobre a estrutura do projeto e gera descrições usando Cohere.
    
    Args:
        path: Caminho do diretório a ser analisado
        api_key: Chave da API Cohere
    
    Returns:
        dict: Estrutura JSON com informações do projeto
    """
    resultado = {
        "path": path,
        "estrutura": []
    }
    
    # Coletar nomes de pastas e arquivos
    for root, dirs, files in os.walk(path):
        # Ignorar __pycache__ e outras pastas desnecessárias
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', 'venv']]
        
        rel_path = os.path.relpath(root, path)
        
        # Processar cada arquivo
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_info = processar_arquivo_python(file_path, rel_path, file, api_key)
                resultado["estrutura"].append(file_info)
            elif not file.startswith('.'):
                # Outros arquivos (json, md, etc)
                file_path = os.path.join(root, file)
                file_info = processar_arquivo_generico(file_path, rel_path, file, api_key)
                resultado["estrutura"].append(file_info)
    
    return resultado


def processar_arquivo_python(file_path, rel_path, filename, api_key):
    """
    Processa um arquivo Python e extrai funções, classes e variáveis.
    """
    info = {
        "tipo": "arquivo_python",
        "nome": filename,
        "caminho": os.path.join(rel_path, filename) if rel_path != '.' else filename,
        "descricao": "",
        "funcoes": [],
        "classes": [],
        "variaveis": []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        # Gerar descrição do arquivo usando Cohere
        system_prompt = "Você é um assistente que analisa código Python e cria descrições concisas."
        user_prompt = f"Descreva brevemente (máximo 2 frases) o propósito deste arquivo Python:\n\n{conteudo[:1000]}"
        
        info["descricao"] = generate(api_key, system_prompt, user_prompt)
        
        # Analisar AST para extrair funções e classes
        try:
            tree = ast.parse(conteudo)
            
            for node in ast.walk(tree):
                # Extrair funções
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "nome": node.name,
                        "linha": node.lineno,
                        "descricao": gerar_descricao_funcao(node, conteudo, api_key)
                    }
                    info["funcoes"].append(func_info)
                
                # Extrair classes
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "nome": node.name,
                        "linha": node.lineno,
                        "descricao": gerar_descricao_classe(node, conteudo, api_key),
                        "metodos": []
                    }
                    
                    # Extrair métodos da classe
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info["metodos"].append({
                                "nome": item.name,
                                "linha": item.lineno
                            })
                    
                    info["classes"].append(class_info)
                
                # Extrair variáveis globais
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            info["variaveis"].append({
                                "nome": target.id,
                                "linha": node.lineno
                            })
        
        except SyntaxError:
            info["descricao"] += " [Arquivo contém erros de sintaxe]"
    
    except Exception as e:
        info["descricao"] = f"Erro ao processar arquivo: {str(e)}"
    
    return info


def processar_arquivo_generico(file_path, rel_path, filename, api_key):
    """
    Processa arquivos não-Python (json, md, txt, etc).
    """
    info = {
        "tipo": "arquivo_generico",
        "nome": filename,
        "caminho": os.path.join(rel_path, filename) if rel_path != '.' else filename,
        "descricao": ""
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            conteudo = f.read(500)  # Ler apenas os primeiros 500 caracteres
        
        system_prompt = "Você é um assistente que analisa arquivos e cria descrições concisas."
        user_prompt = f"Descreva brevemente (1 frase) o propósito deste arquivo '{filename}':\n\n{conteudo}"
        
        info["descricao"] = generate(api_key, system_prompt, user_prompt)
    
    except Exception as e:
        info["descricao"] = f"Arquivo binário ou não legível"
    
    return info


def gerar_descricao_funcao(node, conteudo, api_key):
    """
    Gera descrição para uma função usando Cohere.
    """
    # Extrair docstring se existir
    docstring = ast.get_docstring(node)
    if docstring:
        return docstring.split('\n')[0]  # Primeira linha da docstring
    
    # Caso contrário, extrair código da função
    linhas = conteudo.split('\n')
    inicio = node.lineno - 1
    fim = min(inicio + 10, len(linhas))  # Pegar até 10 linhas
    codigo_funcao = '\n'.join(linhas[inicio:fim])
    
    system_prompt = "Você é um assistente que analisa código Python e cria descrições concisas."
    user_prompt = f"Descreva brevemente (1 frase) o que esta função faz:\n\n{codigo_funcao}"
    
    try:
        return generate(api_key, system_prompt, user_prompt)
    except:
        return "Função sem descrição"


def gerar_descricao_classe(node, conteudo, api_key):
    """
    Gera descrição para uma classe usando Cohere.
    """
    docstring = ast.get_docstring(node)
    if docstring:
        return docstring.split('\n')[0]
    
    linhas = conteudo.split('\n')
    inicio = node.lineno - 1
    fim = min(inicio + 10, len(linhas))
    codigo_classe = '\n'.join(linhas[inicio:fim])
    
    system_prompt = "Você é um assistente que analisa código Python e cria descrições concisas."
    user_prompt = f"Descreva brevemente (1 frase) o propósito desta classe:\n\n{codigo_classe}"
    
    try:
        return generate(api_key, system_prompt, user_prompt)
    except:
        return "Classe sem descrição"


# Exemplo de uso
if __name__ == "__main__":
    import sys
    
    # Carregar API key do config
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
        api_key = config[0]["api_key"]
    
    # Verificar se foi passado um caminho como argumento
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        # Analisar o próprio projeto se nenhum caminho for especificado
        project_path = os.path.dirname(os.path.dirname(__file__))
    
    print(f"Analisando: {project_path}")
    print("Aguarde, isso pode levar alguns minutos...\n")
    
    resultado = cltdds(project_path, api_key)
    
    # Salvar resultado em JSON na mesma pasta que está sendo analisada
    output_path = os.path.join(project_path, "estrutura_projeto.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Estrutura do projeto salva em: {output_path}")
    print(f"✓ Total de arquivos analisados: {len(resultado['estrutura'])}")