# -*- coding: utf-8 -*-
"""
Comando para inicializar o ChromaBuddy no repositório atual
Coleta dados do repositório, configura o assistente e gera estrutura do projeto
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# Adicionar ChromaBuddy ao path
CHROMABUDDY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ChromaBuddy')
sys.path.insert(0, CHROMABUDDY_PATH)

from ChromaBuddy.core.config import ConfigManager
from ChromaBuddy.core.ui import get_ui, get_logger
from ChromaBuddy.core.git import GitIntegration
from ChromaBuddy.locate.dds import cltdds


class AssistantInitializer:
    """Inicializador do ChromaBuddy para repositórios"""
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Inicializa o assistente no repositório
        
        Args:
            repo_path: Caminho do repositório (default: diretório atual)
        """
        self.repo_path = os.path.abspath(repo_path or os.getcwd())
        self.ui = get_ui(theme='monokai')
        self.logger = get_logger(verbose=True)
        
        # Carregar configuração do ChromaBuddy
        config_path = os.path.join(CHROMABUDDY_PATH, 'config.json')
        self.config = ConfigManager(config_path)
        
        self.git_info = None
        self.repo_structure = None
    
    def is_git_repository(self) -> bool:
        """Verifica se o diretório atual é um repositório Git"""
        git_dir = os.path.join(self.repo_path, '.git')
        return os.path.isdir(git_dir)
    
    def collect_git_metadata(self) -> Dict[str, Any]:
        """
        Coleta metadados do repositório Git
        
        Returns:
            Dict com informações do repositório
        """
        if not self.is_git_repository():
            return {
                'is_git': False,
                'message': 'Diretório não é um repositório Git'
            }
        
        try:
            git = GitIntegration(self.repo_path)
            
            # Coletar informações básicas
            metadata = {
                'is_git': True,
                'path': self.repo_path,
                'branch': self._run_git_command(['branch', '--show-current']),
                'remote': self._run_git_command(['remote', 'get-url', 'origin']),
                'status': git.get_status(),
                'last_commit': self._run_git_command(['log', '-1', '--pretty=format:%h - %s (%ar)']),
                'total_commits': self._run_git_command(['rev-list', '--count', 'HEAD']),
            }
            
            self.git_info = metadata
            return metadata
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar metadados Git: {e}")
            return {
                'is_git': True,
                'error': str(e)
            }
    
    def _run_git_command(self, args: list) -> str:
        """Executa comando git e retorna saída"""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip() if result.returncode == 0 else ''
        except Exception:
            return ''
    
    def analyze_repository_structure(self) -> Dict[str, Any]:
        """
        Analisa a estrutura do repositório usando locate/dds.py
        
        Returns:
            Estrutura completa do projeto
        """
        try:
            api_key = self.config.get_api_key()
            
            with self.ui.spinner("Analisando estrutura do repositório..."):
                self.repo_structure = cltdds(self.repo_path, api_key)
            
            # Salvar estrutura em arquivo
            output_path = os.path.join(self.repo_path, 'estrutura_projeto.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.repo_structure, f, indent=2, ensure_ascii=False)
            
            self.logger.success(f"Estrutura salva em: {output_path}")
            return self.repo_structure
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar estrutura: {e}")
            return {
                'error': str(e),
                'path': self.repo_path,
                'estrutura': []
            }
    
    def count_files_by_type(self) -> Dict[str, int]:
        """Conta arquivos por tipo no repositório"""
        if not self.repo_structure:
            return {}
        
        counts = {}
        for item in self.repo_structure.get('estrutura', []):
            tipo = item.get('tipo', 'desconhecido')
            counts[tipo] = counts.get(tipo, 0) + 1
        
        return counts
    
    def display_summary(self):
        """Exibe resumo bonito da inicialização"""
        # Cabeçalho
        self.ui.print("\n")
        self.ui.panel(
            "[bold cyan]ChromaBuddy PRO[/bold cyan]\n"
            "[dim]Assistente de Codificação com IA[/dim]",
            title="Inicialização"
        )
        
        # Informações do repositório
        if self.git_info and self.git_info.get('is_git'):
            git_content = f"""
[bold]Caminho:[/bold] {self.git_info['path']}
[bold]Branch:[/bold] {self.git_info.get('branch', 'N/A')}
[bold]Remote:[/bold] {self.git_info.get('remote', 'N/A')}
[bold]Commits:[/bold] {self.git_info.get('total_commits', 'N/A')}
[bold]Último commit:[/bold] {self.git_info.get('last_commit', 'N/A')}
"""
            self.ui.panel(git_content.strip(), title="Informações Git", border_style="green")
        else:
            self.ui.panel(
                f"[yellow]Diretório não é repositório Git[/yellow]\n[bold]Caminho:[/bold] {self.repo_path}",
                title="Informações do Diretório",
                border_style="yellow"
            )
        
        # Estatísticas da estrutura
        if self.repo_structure:
            total_files = len(self.repo_structure.get('estrutura', []))
            file_counts = self.count_files_by_type()
            
            stats_content = f"[bold]Total de arquivos analisados:[/bold] {total_files}\n\n"
            for tipo, count in file_counts.items():
                stats_content += f"  • {tipo}: {count}\n"
            
            self.ui.panel(stats_content.strip(), title="Estrutura do Projeto", border_style="blue")
        
        # Status
        status_info = self.git_info.get('status', {}) if self.git_info else {}
        if status_info:
            modified = len(status_info.get('modified', []))
            untracked = len(status_info.get('untracked', []))
            
            status_content = f"""
[bold]Arquivos modificados:[/bold] {modified}
[bold]Arquivos não rastreados:[/bold] {untracked}
"""
            self.ui.panel(status_content.strip(), title="Status Git", border_style="magenta")
        
        # Próximos passos
        next_steps = """
1. Execute o assistente: [bold cyan]python -m ChromaBuddy.chat[/bold cyan]
2. Use comandos como [bold]/help[/bold], [bold]/scan[/bold], [bold]/analyze[/bold]
3. Mencione arquivos com [bold]@arquivo.py[/bold] para contexto
4. Configure preferências com [bold]/config[/bold]
"""
        self.ui.panel(next_steps.strip(), title="Próximos Passos", border_style="green")
    
    def initialize(self) -> Dict[str, Any]:
        """
        Executa inicialização completa do assistente
        
        Returns:
            Resultado da inicialização
        """
        try:
            self.ui.print("\n[bold cyan]Inicializando ChromaBuddy no repositório...[/bold cyan]\n")
            
            # 1. Coletar metadados Git
            with self.ui.spinner("Coletando informações do repositório..."):
                self.collect_git_metadata()
            
            # 2. Analisar estrutura
            self.analyze_repository_structure()
            
            # 3. Exibir resumo
            self.display_summary()
            
            return {
                'success': True,
                'git_info': self.git_info,
                'structure': self.repo_structure,
                'message': 'ChromaBuddy inicializado com sucesso'
            }
            
        except Exception as e:
            self.logger.error(f"Falha na inicialização: {e}")
            return {
                'success': False,
                'error': str(e)
            }


def init_assistant(repo_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Função principal para inicializar o assistente
    
    Args:
        repo_path: Caminho do repositório (default: diretório atual)
    
    Returns:
        Resultado da inicialização
    """
    initializer = AssistantInitializer(repo_path)
    return initializer.initialize()


if __name__ == '__main__':
    """Entry point para CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Inicializa ChromaBuddy PRO no repositório atual'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default=None,
        help='Caminho do repositório (padrão: diretório atual)'
    )
    
    args = parser.parse_args()
    
    result = init_assistant(args.path)
    
    sys.exit(0 if result.get('success') else 1)
