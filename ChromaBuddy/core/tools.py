# -*- coding: utf-8 -*-
import re
import json

class SmartTools:
    @staticmethod
    def regex_builder(description, api_key):
        # gerar regex a partir de descrição
        from models.cohe import generate
        
        sys_prompt = "Você é um especialista em regex. Gere apenas a expressão regular, sem explicações."
        user_prompt = f"Gere regex para: {description}"
        
        try:
            regex = generate(api_key, sys_prompt, user_prompt).strip()
            # limpar
            regex = regex.replace('```', '').replace('regex:', '').strip()
            return regex
        except:
            return None
    
    @staticmethod
    def test_regex(pattern, test_strings):
        # testar regex
        results = []
        try:
            compiled = re.compile(pattern)
            for s in test_strings:
                match = compiled.search(s)
                results.append({
                    'string': s,
                    'matched': bool(match),
                    'groups': match.groups() if match else None
                })
        except re.error as e:
            return {'error': str(e)}
        
        return results
    
    @staticmethod
    def extract_with_regex(pattern, text):
        # extrair dados com regex
        try:
            return re.findall(pattern, text)
        except:
            return []
    
    @staticmethod
    def replace_with_regex(pattern, replacement, text):
        # substituir com regex
        try:
            return re.sub(pattern, replacement, text)
        except:
            return text
    
    @staticmethod
    def format_json(data, indent=2):
        # formatar JSON
        try:
            if isinstance(data, str):
                data = json.loads(data)
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except:
            return data
    
    @staticmethod
    def minify_json(data):
        # minificar JSON
        try:
            if isinstance(data, str):
                data = json.loads(data)
            return json.dumps(data, separators=(',', ':'))
        except:
            return data
    
    @staticmethod
    def transform_data(data, transformation, api_key):
        # transformação de dados com IA
        from models.cohe import generate
        
        sys_prompt = "Transforme os dados conforme solicitado. Retorne apenas o resultado."
        user_prompt = f"Dados:\n{data}\n\nTransformação: {transformation}"
        
        try:
            return generate(api_key, sys_prompt, user_prompt).strip()
        except:
            return data
    
    @staticmethod
    def csv_to_dict(csv_text):
        # converter CSV para dict
        lines = csv_text.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = [h.strip() for h in lines[0].split(',')]
        result = []
        
        for line in lines[1:]:
            values = [v.strip() for v in line.split(',')]
            if len(values) == len(headers):
                result.append(dict(zip(headers, values)))
        
        return result
    
    @staticmethod
    def dict_to_csv(data):
        # converter dict para CSV
        if not data:
            return ""
        
        headers = list(data[0].keys())
        lines = [','.join(headers)]
        
        for row in data:
            lines.append(','.join(str(row.get(h, '')) for h in headers))
        
        return '\n'.join(lines)
    
    @staticmethod
    def generate_sample_data(schema, count=10):
        # gerar dados de exemplo
        import random
        import string
        
        data = []
        for _ in range(count):
            item = {}
            for key, dtype in schema.items():
                if dtype == 'string':
                    item[key] = ''.join(random.choices(string.ascii_letters, k=8))
                elif dtype == 'int':
                    item[key] = random.randint(1, 100)
                elif dtype == 'float':
                    item[key] = round(random.uniform(1, 100), 2)
                elif dtype == 'bool':
                    item[key] = random.choice([True, False])
            data.append(item)
        
        return data
