# -*- coding: utf-8 -*-
import json
from pathlib import Path

class TemplateSystem:
    def __init__(self):
        self.templates = self._load_default_templates()
    
    def _load_default_templates(self):
        return {
            'flask_route': """@app.route('{route}', methods=['{method}'])
def {name}():
    try:
        # TODO: implementar lógica
        return jsonify({{'success': True}})
    except Exception as e:
        return jsonify({{'error': str(e)}}), 500""",
            
            'fastapi_route': """@app.{method}("{route}")
async def {name}():
    try:
        # TODO: implementar lógica
        return {{"success": True}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))""",
            
            'class_basic': """class {name}:
    def __init__(self{params}):
        {init_body}
    
    def __str__(self):
        return f"<{name}>"
    
    def __repr__(self):
        return self.__str__()""",
            
            'dataclass': """from dataclasses import dataclass

@dataclass
class {name}:
    {fields}""",
            
            'pytest_test': """import pytest

def test_{name}():
    # Arrange
    {arrange}
    
    # Act
    {act}
    
    # Assert
    {assert_stmt}""",
            
            'async_function': """async def {name}({params}):
    '''
    {docstring}
    '''
    try:
        # TODO: implementar
        return None
    except Exception as e:
        raise""",
            
            'property': """@property
def {name}(self):
    return self._{name}

@{name}.setter
def {name}(self, value):
    self._{name} = value""",
            
            'context_manager': """class {name}:
    def __enter__(self):
        # TODO: setup
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: cleanup
        pass""",
            
            'decorator': """def {name}(func):
    def wrapper(*args, **kwargs):
        # Before
        result = func(*args, **kwargs)
        # After
        return result
    return wrapper""",
            
            'cli_command': """import click

@click.command()
@click.argument('{arg}')
@click.option('--{option}', default={default}, help='{help}')
def {name}({arg}, {option}):
    '''
    {docstring}
    '''
    click.echo(f"Executando {name}...")""",
        }
    
    def get_template(self, template_name):
        return self.templates.get(template_name, None)
    
    def render_template(self, template_name, **kwargs):
        template = self.get_template(template_name)
        if not template:
            return None
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"Erro: parâmetro faltando - {e}"
    
    def list_templates(self):
        return list(self.templates.keys())
    
    def add_custom_template(self, name, template_code):
        self.templates[name] = template_code
    
    def generate_boilerplate(self, project_type):
        boilerplates = {
            'flask': {
                'app.py': """from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'message': 'Hello World'})

if __name__ == '__main__':
    app.run(debug=True)""",
                
                'requirements.txt': """flask>=2.0.0
python-dotenv>=0.19.0""",
                
                'config.py': """import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    DEBUG = True"""
            },
            
            'fastapi': {
                'main.py': """from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)""",
                
                'requirements.txt': """fastapi>=0.95.0
uvicorn[standard]>=0.20.0"""
            },
            
            'cli': {
                'cli.py': """import click

@click.group()
def cli():
    pass

@cli.command()
def hello():
    click.echo('Hello!')

if __name__ == '__main__':
    cli()""",
                
                'requirements.txt': """click>=8.0.0"""
            }
        }
        
        return boilerplates.get(project_type, {})
    
    def create_snippet(self, name, code, description=""):
        # criar snippet personalizado
        return {
            'name': name,
            'code': code,
            'description': description
        }
    
    def expand_abbreviation(self, abbrev):
        # expandir abreviações (tipo emmet)
        expansions = {
            'pdb': 'import pdb; pdb.set_trace()',
            'ipdb': 'import ipdb; ipdb.set_trace()',
            'pprint': 'from pprint import pprint',
            'dt': 'from datetime import datetime',
            'pd': 'import pandas as pd',
            'np': 'import numpy as np',
            'plt': 'import matplotlib.pyplot as plt',
            'req': 'import requests',
            'json': 'import json',
            'os': 'import os',
            'sys': 'import sys',
            'main': """if __name__ == '__main__':
    pass""",
            'try': """try:
    pass
except Exception as e:
    print(f"Error: {e}")""",
            'async': """async def function_name():
    pass""",
        }
        
        return expansions.get(abbrev, abbrev)
