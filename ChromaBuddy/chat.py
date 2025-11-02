# -*- coding: utf-8 -*-
"""
ChromaBuddy PRO - Interface Principal de Chat
Assistente Profissional de Codificação com IA
"""

import os
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path

from models.cohe import generate
from core.tokenizer import tokenizer
from core.execute import execute
from core.test import test
from core.memory import MemorySystem
from core.test_gen import TestGenerator
from core.analyzer import CodeAnalyzer
from core.cache import get_cache
from core.mentions import MentionSystem
from core.batch import BatchOperations
from core.docs import DocumentationGenerator
from core.git import GitIntegration
from core.performance import PerformanceOptimizer
from core.tools import SmartTools
from core.templates import TemplateSystem
from core.config import ConfigManager
from core.ui import get_ui, get_logger
from core.deep_think import DeepThinkMode


class ChromaBuddyPro:
    """Classe principal da aplicação ChromaBuddy PRO"""
    
    def __init__(self, config_manager: ConfigManager, project_root: str):
        """
        Inicializa o ChromaBuddy PRO
        
        Args:
            config_manager: Instância do gerenciador de configuração
            project_root: Diretório raiz do projeto
        """
        self.config = config_manager
        self.project_root = project_root
        self.ui = get_ui(theme=self.config.get('theme', 'monokai'))
        self.logger = get_logger(verbose=True)
        
        # Inicializar subsistemas
        try:
            api_key = self.config.get_api_key()
            
            with self.ui.spinner("Inicializando subsistemas..."):
                self.memory = MemorySystem()
                self.test_gen = TestGenerator(api_key)
                self.analyzer = CodeAnalyzer()
                self.mentions = MentionSystem(project_root)
                self.batch_ops = BatchOperations(project_root)
                self.doc_gen = DocumentationGenerator(api_key)
                self.git_integration = GitIntegration(project_root)
                self.perf_optimizer = PerformanceOptimizer()
                self.smart_tools = SmartTools()
                self.templates = TemplateSystem()
                
                # Modo pensamento profundo (opcional)
                if self.config.get('deep_think_enabled', False):
                    iterations = self.config.get('deep_think_iterations', 3)
                    self.deep_think = DeepThinkMode(api_key, iterations)
                else:
                    self.deep_think = None
            
            self.session_stats = {
                'files_modified': 0,
                'tests_generated': 0,
                'bugs_fixed': 0,
                'mentions_used': 0,
                'commands_run': 0
            }
            
            self.logger.success("ChromaBuddy PRO inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Falha na inicialização: {e}")
            raise
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """
        Processa entrada do usuário
        
        Args:
            user_input: Comando ou solicitação do usuário
            
        Returns:
            Dicionário de resultado
        """
        try:
            # Tratar comandos especiais
            if user_input.startswith('/'):
                self.session_stats['commands_run'] += 1
                return self._handle_command(user_input)
            
            # Expandir menções @
            expanded_prompt = user_input
            mention_info = None
            
            if '@' in user_input:
                with self.ui.spinner("Resolvendo menções..."):
                    expanded_prompt, mention_info = self.mentions.expand_prompt(user_input)
                
                if mention_info:
                    self.session_stats['mentions_used'] += 1
                    files = mention_info.get('files_count', 0)
                    symbols = mention_info.get('symbols_count', 0)
                    self.logger.info(f"Menções resolvidas: {files} arquivos, {symbols} símbolos")
            
            # Modo pensamento profundo (se habilitado)
            if self.deep_think and self.config.get('deep_think_enabled'):
                context = {
                    'project_root': self.project_root,
                    'mentions': mention_info
                }
                plan = self.deep_think.think(expanded_prompt, context)
                
                if not self.ui.confirm("Prosseguir com execução?", default=True):
                    return {'status': 'cancelled'}
            
            # Tokenizar solicitação
            with self.ui.spinner("Analisando solicitação..."):
                result = tokenizer(expanded_prompt, self.config.get_api_key(), self.project_root)
            
            if 'error' in result:
                self.logger.error(result['error'])
                return {'error': result['error']}
            
            # Exibir análise
            self._display_analysis(result, mention_info)
            
            # Confirmar execução
            if self.config.get('diff_approval', True):
                if not self.ui.confirm("Aplicar mudanças?", default=True):
                    return {'status': 'cancelled'}
            
            # Executar mudanças
            with self.ui.spinner("Executando mudanças..."):
                changes = execute(result, self.config.get_api_key(), self.project_root)
            
            if changes.get('modified', 0) > 0:
                self._display_changes(changes)
                
                # Auto-teste se habilitado
                if self.config.get('auto_test', True):
                    test_result = self._run_tests(changes, result)
                    self._display_test_results(test_result)
            
            # Salvar na memória
            self.memory.add_interaction({
                'request': user_input,
                'result': result,
                'changes': changes
            })
            
            return {'status': 'success', 'changes': changes}
            
        except Exception as e:
            self.logger.error(f"Command processing failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _display_analysis(self, result: Dict[str, Any], mention_info: Optional[Dict]) -> None:
        """Display analysis results"""
        self.ui.rule("Analysis Results")
        
        self.ui.print(f"[bold]Intent:[/bold] {result.get('intention', 'Unknown')}")
        self.ui.print(f"[bold]Target Files:[/bold] {', '.join(result.get('target_files', []))}")
        
        context = result.get('context', {})
        self.ui.print(
            f"[bold]Context:[/bold] {context.get('total_files', 0)} files, "
            f"{context.get('total_symbols', 0)} symbols"
        )
        
        cache_stats = result.get('cache_stats', {})
        self.ui.print(f"[bold]Cache:[/bold] {cache_stats.get('rate', 'N/A')}")
        
        if mention_info:
            mentions = mention_info.get('mentions', {}).get('raw', [])
            self.ui.print(f"[bold]Mentions:[/bold] {', '.join(mentions)}")
        
        plan = result.get('edit_plan', 'No plan available')
        self.ui.panel(plan, title="Execution Plan", border_style="cyan")
    
    def _display_changes(self, changes: Dict[str, Any]) -> None:
        """Display file changes"""
        modified = changes.get('modified', 0)
        total = changes.get('total', 0)
        
        self.logger.success(f"{modified} of {total} files modified")
        
        for change in changes.get('changes', []):
            if change['status'] == 'modificado':
                file = change['file']
                details = change.get('details', 'modified')
                self.ui.print(f"  [green]Modified:[/green] {file} - {details}")
                self.session_stats['files_modified'] += 1
    
    def _run_tests(self, changes: Dict[str, Any], tokenizer_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run tests on modified files"""
        with self.ui.spinner("Running tests..."):
            return test(changes, tokenizer_result, self.config.get_api_key(), self.project_root)
    
    def _display_test_results(self, test_result: Dict[str, Any]) -> None:
        """Display test results"""
        self.ui.rule("Test Results")
        
        for result in test_result.get('results', []):
            file = result['file']
            status = result['status']
            message = result.get('message', '')
            
            if status == 'sucesso':
                self.ui.print(f"  [green]PASS:[/green] {file} - {message}")
            elif status == 'erro':
                attempts = result.get('attempts', 0)
                self.ui.print(f"  [red]FAIL:[/red] {file} - Failed after {attempts} attempts")
                self.session_stats['bugs_fixed'] += attempts - 1
    
    def _handle_command(self, command: str) -> Dict[str, Any]:
        """Handle special commands"""
        parts = command[1:].split()
        if not parts:
            return {'status': 'error', 'error': 'Empty command'}
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        try:
            if cmd == 'help':
                self._show_help()
            elif cmd == 'stats':
                self._show_stats()
            elif cmd == 'config':
                self._config_command(args)
            elif cmd == 'analyze' and args:
                self._analyze_file(args[0])
            elif cmd == 'memory':
                self._show_memory()
            elif cmd == 'cache':
                self._cache_command(args)
            elif cmd == 'git':
                self._git_command(args)
            elif cmd == 'rename' and len(args) >= 2:
                self._batch_rename(args[0], args[1])
            elif cmd == 'docs' and args:
                self._generate_docs(args[0])
            elif cmd == 'template':
                self._use_template(args)
            elif cmd == 'regex':
                self._regex_tool(args)
            elif cmd == 'perf' and args:
                self._performance_check(args[0])
            elif cmd == 'format':
                self._format_all()
            elif cmd == 'deep':
                self._toggle_deep_think()
            elif cmd == 'cd':
                self._change_directory(args)
            elif cmd == 'pwd':
                self._show_current_directory()
            elif cmd == 'scan':
                self._force_scan_project()
            else:
                self.logger.error(f"Comando desconhecido: {cmd}")
                self._show_help()
            
            return {'status': 'ok'}
            
        except Exception as e:
            self.logger.error(f"Comando falhou: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _show_help(self) -> None:
        """Exibir informações de ajuda"""
        self.ui.rule("Comandos Disponíveis")
        
        commands = [
            ("Informações", [
                ("/stats", "Estatísticas da sessão"),
                ("/memory", "Ver padrões aprendidos"),
                ("/config", "Configurar ajustes"),
                ("/help", "Mostrar esta ajuda")
            ]),
            ("Navegação", [
                ("/pwd", "Mostrar diretório atual"),
                ("/cd <caminho>", "Mudar diretório de trabalho"),
                ("/scan", "Analisar estrutura do projeto")
            ]),
            ("Análise", [
                ("/analyze <arquivo>", "Analisar qualidade de código"),
                ("/perf <arquivo>", "Análise de performance")
            ]),
            ("Documentação", [
                ("/docs <arquivo>", "Gerar documentação")
            ]),
            ("Ferramentas", [
                ("/template [nome]", "Templates de código"),
                ("/regex [cmd]", "Ferramentas regex"),
                ("/format", "Formatar todos arquivos")
            ]),
            ("Operações em Lote", [
                ("/rename <antigo> <novo>", "Renomear símbolo")
            ]),
            ("Git", [
                ("/git <cmd>", "Integração Git")
            ]),
            ("Cache", [
                ("/cache [stats|clear]", "Gerenciar cache")
            ]),
            ("Modo", [
                ("/deep", "Alternar modo pensamento profundo")
            ])
        ]
        
        for category, cmds in commands:
            self.ui.print(f"\n[bold cyan]{category}:[/bold cyan]")
            for cmd, desc in cmds:
                self.ui.print(f"  {cmd:<25} {desc}")
        
        self.ui.print("\n[bold]Recursos Especiais:[/bold]")
        self.ui.print("  Menções @ - Use @arquivo.py, @Classe, @funcao para contexto")
        self.ui.print("  Linguagem natural - Apenas descreva o que você quer")
    
    def _show_stats(self) -> None:
        """Exibir estatísticas da sessão"""
        self.ui.rule("Estatísticas da Sessão")
        
        stats = [
            ("Files Modified", self.session_stats['files_modified']),
            ("Tests Generated", self.session_stats['tests_generated']),
            ("Bugs Fixed", self.session_stats['bugs_fixed']),
            ("Mentions Used", self.session_stats['mentions_used']),
            ("Commands Run", self.session_stats['commands_run'])
        ]
        
        for label, value in stats:
            self.ui.print(f"[bold]{label}:[/bold] {value}")
        
        # Cache stats
        cache = get_cache()
        cache_stats = cache.get_stats()
        
        self.ui.print(f"\n[bold]Cache:[/bold]")
        self.ui.print(f"  Hit Rate: {cache_stats.get('hit_rate', 0):.1f}%")
        self.ui.print(f"  Entries: {cache_stats.get('entries', 0)}")
        self.ui.print(f"  Memory: {cache_stats.get('memory_mb', 0):.1f} MB")
        
        # Memory patterns
        patterns = self.memory.get_patterns()
        if patterns:
            self.ui.print(f"\n[bold]Learning:[/bold]")
            self.ui.print(f"  Interactions: {len(self.memory.history)}")
            self.ui.print(f"  Patterns Detected: {len(patterns)}")
    
    def _config_command(self, args: List[str]) -> None:
        """Handle config command"""
        if not args or args[0] == 'show':
            self.ui.print(self.config.display_config())
        elif args[0] == 'setup':
            self.config.interactive_setup()
        elif args[0] == 'set' and len(args) >= 3:
            key = args[1]
            value = ' '.join(args[2:])
            
            # Parse value
            if value.lower() in ['true', 'yes', 'y']:
                value = True
            elif value.lower() in ['false', 'no', 'n']:
                value = False
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '', 1).isdigit():
                value = float(value)
            
            self.config.set(key, value)
            self.logger.success(f"Config updated: {key} = {value}")
        else:
            self.ui.print("Usage:")
            self.ui.print("  /config show   - Show current configuration")
            self.ui.print("  /config setup  - Interactive setup")
            self.ui.print("  /config set <key> <value>  - Set specific value")
    
    def _analyze_file(self, filename: str) -> None:
        """Analyze code quality of file"""
        file_path = os.path.join(self.project_root, filename)
        
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {filename}")
            return
        
        with self.ui.spinner(f"Analyzing {filename}..."):
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            analysis = self.analyzer.analyze(code)
        
        self._display_analysis_results(filename, analysis)
    
    def _display_analysis_results(self, filename: str, analysis: Dict[str, Any]) -> None:
        """Display code analysis results"""
        self.ui.rule(f"Analysis: {filename}")
        
        score = analysis.get('quality_score', 0)
        score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
        
        self.ui.print(f"[bold]Quality Score:[/bold] [{score_color}]{score}/100[/{score_color}]")
        
        issues = analysis.get('issues', [])
        if issues:
            self.ui.print(f"\n[bold]Issues Found:[/bold] {len(issues)}")
            for issue in issues[:10]:  # Show first 10
                severity = issue.get('severity', 'info')
                color = "red" if severity == 'high' else "yellow" if severity == 'medium' else "blue"
                self.ui.print(f"  [{color}]{issue['type']}[/{color}]: {issue['message']}")
        
        suggestions = analysis.get('suggestions', [])
        if suggestions:
            self.ui.print(f"\n[bold]Suggestions:[/bold]")
            for suggestion in suggestions[:5]:  # Show first 5
                self.ui.print(f"  - {suggestion}")
    
    def _show_memory(self) -> None:
        """Display memory and patterns"""
        self.ui.rule("Learning System")
        
        self.ui.print(f"[bold]Total Interactions:[/bold] {len(self.memory.history)}")
        
        patterns = self.memory.get_patterns()
        if patterns:
            self.ui.print(f"\n[bold]Detected Patterns:[/bold]")
            for pattern in patterns[:10]:
                self.ui.print(f"  - {pattern}")
        
        prefs = self.memory.get_preferences()
        if prefs:
            self.ui.print(f"\n[bold]User Preferences:[/bold]")
            for key, value in list(prefs.items())[:5]:
                self.ui.print(f"  {key}: {value}")
    
    def _cache_command(self, args: List[str]) -> None:
        """Handle cache command"""
        cache = get_cache()
        
        if not args or args[0] == 'stats':
            stats = cache.get_stats()
            self.ui.print(f"[bold]Cache Statistics:[/bold]")
            self.ui.print(f"  Hit Rate: {stats.get('hit_rate', 0):.1f}%")
            self.ui.print(f"  Total Hits: {stats.get('hits', 0)}")
            self.ui.print(f"  Total Misses: {stats.get('misses', 0)}")
            self.ui.print(f"  Entries: {stats.get('entries', 0)}")
            self.ui.print(f"  Memory: {stats.get('memory_mb', 0):.1f} MB")
        
        elif args[0] == 'clear':
            cache.clear()
            self.logger.success("Cache cleared")
    
    def _toggle_deep_think(self) -> None:
        """Toggle deep think mode"""
        current = self.config.get('deep_think_enabled', False)
        new_value = not current
        
        self.config.set('deep_think_enabled', new_value)
        
        if new_value:
            if not self.deep_think:
                iterations = self.config.get('deep_think_iterations', 3)
                self.deep_think = DeepThinkMode(self.config.get_api_key(), iterations)
            self.logger.success("Deep Think Mode ENABLED")
        else:
            self.logger.info("Deep Think Mode DISABLED")
    
    # Import other command methods from original chat.py
    def _git_command(self, args: List[str]) -> None:
        """Execute Git commands"""
        if not args:
            self.ui.print("\nGit Commands:")
            self.ui.print("  /git status       - Repository status")
            self.ui.print("  /git diff         - Show differences")
            self.ui.print("  /git commit       - AI-powered commit")
            self.ui.print("  /git branch <name> - Create branch")
            self.ui.print("  /git log          - Commit history")
            self.ui.print("  /git pr           - Generate PR description")
            return
        
        cmd = args[0].lower()
        
        try:
            if cmd == 'status':
                with self.ui.spinner("Checking status..."):
                    status = self.git_integration.status()
                self.ui.print(status)
            
            elif cmd == 'diff':
                with self.ui.spinner("Getting diff..."):
                    diff = self.git_integration.diff()
                self.ui.code(diff, language="diff")
            
            elif cmd == 'commit':
                with self.ui.spinner("Generating commit message..."):
                    result = self.git_integration.auto_commit(self.config.get_api_key())
                self.logger.success(result)
            
            elif cmd == 'branch' and len(args) > 1:
                branch_name = args[1]
                result = self.git_integration.create_branch(branch_name)
                self.logger.success(result)
            
            elif cmd == 'log':
                import subprocess
                result = subprocess.run(
                    ['git', 'log', '--oneline', '-10'],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                self.ui.print(f"\nLast 10 commits:\n{result.stdout}")
            
            elif cmd == 'pr':
                with self.ui.spinner("Generating PR description..."):
                    desc = self.git_integration.generate_pr_description(self.config.get_api_key())
                self.ui.panel(desc, title="Pull Request Description", border_style="green")
            
            else:
                self.logger.error(f"Unknown git command: {cmd}")
        
        except Exception as e:
            self.logger.error(f"Git command failed: {e}")
    
    def _batch_rename(self, old_name: str, new_name: str) -> None:
        """Rename symbol across all files"""
        with self.ui.spinner(f"Renaming '{old_name}' to '{new_name}'..."):
            result = self.batch_ops.rename_symbol(old_name, new_name, self.project_root)
        
        self.logger.success(
            f"Renamed in {result['files_modified']} files "
            f"({result['occurrences_renamed']} occurrences)"
        )
        
        if result.get('files'):
            self.ui.print("\nModified files:")
            for file in result['files']:
                self.ui.print(f"  - {file}")
    
    def _generate_docs(self, filename: str) -> None:
        """Generate documentation for file"""
        file_path = os.path.join(self.project_root, filename)
        
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {filename}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        with self.ui.spinner("Generating docstrings..."):
            documented_code = self.doc_gen.generate_docstrings(code, self.config.get_api_key())
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(documented_code)
        
        self.logger.success(f"Docstrings added to {filename}")
        
        # Generate API docs
        with self.ui.spinner("Generating API documentation..."):
            api_docs = self.doc_gen.generate_api_docs(code, filename)
        
        docs_path = os.path.join(self.project_root, 'docs', f'{filename}.md')
        os.makedirs(os.path.dirname(docs_path), exist_ok=True)
        
        with open(docs_path, 'w', encoding='utf-8') as f:
            f.write(api_docs)
        
        self.logger.success(f"API documentation saved to docs/{filename}.md")
    
    def _use_template(self, args: List[str]) -> None:
        """Use code template"""
        if not args:
            self.ui.print("\nAvailable Templates:")
            for name, template in self.templates.templates.items():
                desc = template.get('description', 'No description')
                self.ui.print(f"  {name:<20} {desc}")
            return
        
        template_name = args[0]
        
        if template_name not in self.templates.templates:
            self.logger.error(f"Template not found: {template_name}")
            return
        
        template = self.templates.templates[template_name]
        params = {}
        
        self.ui.print(f"\n{template.get('description', 'Template')}")
        self.ui.print("Fill parameters (Enter to skip):\n")
        
        for param in template.get('params', []):
            value = self.ui.prompt(param)
            if value:
                params[param] = value
        
        code = self.templates.render_template(template_name, **params)
        
        self.ui.rule("Generated Code")
        self.ui.code(code, language="python")
        
        if self.ui.confirm("Save to file?", default=False):
            filename = self.ui.prompt("Filename")
            if filename:
                file_path = os.path.join(self.project_root, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                self.logger.success(f"Saved to {filename}")
    
    def _regex_tool(self, args: List[str]) -> None:
        """Regex tools"""
        if not args:
            self.ui.print("\nRegex Tools:")
            self.ui.print("  /regex build <description>  - Create regex from description")
            self.ui.print("  /regex test <pattern> <text> - Test regex pattern")
            return
        
        cmd = args[0].lower()
        
        if cmd == 'build' and len(args) > 1:
            description = ' '.join(args[1:])
            
            with self.ui.spinner("Generating regex..."):
                pattern = self.smart_tools.regex_builder(description, self.config.get_api_key())
            
            self.ui.print(f"\n[bold]Pattern:[/bold] {pattern.get('pattern', 'N/A')}")
            self.ui.print(f"[bold]Explanation:[/bold] {pattern.get('explanation', 'N/A')}")
            
            examples = pattern.get('examples', [])
            if examples:
                self.ui.print("\n[bold]Examples:[/bold]")
                for ex in examples:
                    self.ui.print(f"  - {ex}")
        
        elif cmd == 'test' and len(args) > 2:
            pattern = args[1]
            text = ' '.join(args[2:])
            
            result = self.smart_tools.test_regex(pattern, text)
            
            self.ui.print(f"\n[bold]Pattern:[/bold] {pattern}")
            self.ui.print(f"[bold]Text:[/bold] {text}")
            
            if result.get('matches'):
                self.ui.print("[bold green]MATCH[/bold green]")
                
                groups = result.get('groups', [])
                if groups:
                    self.ui.print("\n[bold]Captured Groups:[/bold]")
                    for i, group in enumerate(groups):
                        self.ui.print(f"  Group {i}: {group}")
            else:
                self.ui.print("[bold red]NO MATCH[/bold red]")
        
        else:
            self.logger.error("Invalid usage. Use /regex for help")
    
    def _performance_check(self, filename: str) -> None:
        """Analyze file performance"""
        file_path = os.path.join(self.project_root, filename)
        
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {filename}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        with self.ui.spinner(f"Analyzing performance of {filename}..."):
            bottlenecks = self.perf_optimizer.analyze_bottlenecks(code)
            optimizations = self.perf_optimizer.suggest_optimizations(
                code,
                self.config.get_api_key()
            )
        
        self.ui.rule(f"Performance Analysis: {filename}")
        
        if bottlenecks:
            self.ui.print(f"\n[bold]Bottlenecks Found:[/bold] {len(bottlenecks)}")
            for b in bottlenecks:
                severity = b.get('severity', 'medium')
                color = "red" if severity == 'high' else "yellow"
                
                self.ui.print(f"\n  Line {b.get('line', '?')}: [{color}]{b.get('issue', 'Unknown')}[/{color}]")
                self.ui.print(f"  Suggestion: {b.get('suggestion', 'N/A')}")
        else:
            self.logger.success("No obvious bottlenecks found")
        
        if optimizations:
            self.ui.print(f"\n[bold]Sugestões de Otimização:[/bold]")
            for opt in optimizations:
                self.ui.print(f"\n  {opt.get('title', 'Otimização')}")
                self.ui.print(f"  {opt.get('description', 'Sem descrição')}")
                
                if opt.get('code'):
                    self.ui.code(opt['code'], language="python", line_numbers=False)
    
    def _format_all(self) -> None:
        """Formatar todos os arquivos Python"""
        with self.ui.spinner("Formatando todos os arquivos Python..."):
            result = self.batch_ops.format_all_files(self.project_root)
        
        self.logger.success(f"{result['files_formatted']} arquivos formatados")
        
        if result.get('files'):
            self.ui.print("\nArquivos formatados:")
            for file in result['files']:
                self.ui.print(f"  - {file}")
    
    def _change_directory(self, args: List[str]) -> None:
        """Mudar diretório de trabalho"""
        if not args:
            self.ui.print(f"\n[bold]Diretório atual:[/bold] {self.project_root}")
            self.ui.print("\nUso: /cd <caminho>")
            self.ui.print("Exemplos:")
            self.ui.print("  /cd ..                    # Voltar um nível")
            self.ui.print("  /cd c:\\projetos\\meuapp   # Caminho absoluto")
            self.ui.print("  /cd subpasta              # Caminho relativo")
            return
        
        new_path = ' '.join(args)
        
        # Se for caminho relativo, resolver a partir do diretório atual
        if not os.path.isabs(new_path):
            new_path = os.path.join(self.project_root, new_path)
        
        # Normalizar caminho
        new_path = os.path.normpath(new_path)
        
        # Verificar se o diretório existe
        if not os.path.exists(new_path):
            self.logger.error(f"Diretório não encontrado: {new_path}")
            return
        
        if not os.path.isdir(new_path):
            self.logger.error(f"Não é um diretório: {new_path}")
            return
        
        # Atualizar diretório de trabalho
        old_path = self.project_root
        self.project_root = new_path
        
        # Reinicializar subsistemas que dependem do project_root
        try:
            self.mentions = MentionSystem(new_path)
            self.batch_ops = BatchOperations(new_path)
            self.git_integration = GitIntegration(new_path)
            
            self.logger.success(f"Diretório alterado: {old_path} -> {new_path}")
            
            # Mostrar informações do novo diretório
            python_files = list(Path(new_path).rglob('*.py'))
            self.ui.print(f"\n[bold]Novo workspace:[/bold]")
            self.ui.print(f"  Caminho: {new_path}")
            self.ui.print(f"  Arquivos Python: {len(python_files)}")
            
            # Executar dds.py automaticamente para analisar estrutura
            self._analyze_project_structure(new_path)
            
        except Exception as e:
            # Reverter em caso de erro
            self.project_root = old_path
            self.logger.error(f"Falha ao mudar diretório: {e}")
    
    def _analyze_project_structure(self, project_path: str) -> None:
        """Analisa a estrutura do projeto usando dds.py"""
        estrutura_path = os.path.join(project_path, "estrutura_projeto.json")
        
        # Verificar se já existe e está recente (menos de 1 hora)
        if os.path.exists(estrutura_path):
            import time
            file_age = time.time() - os.path.getmtime(estrutura_path)
            if file_age < 3600:  # 1 hora
                self.logger.info("Estrutura do projeto já existe e está atualizada")
                return
        
        # Executar análise
        try:
            with self.ui.spinner("Analisando estrutura do projeto..."):
                from locate.dds import cltdds
                
                resultado = cltdds(project_path, self.config.get_api_key())
                
                # Salvar resultado
                with open(estrutura_path, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(resultado, f, indent=2, ensure_ascii=False)
            
            self.logger.success(f"Estrutura analisada: {len(resultado['estrutura'])} arquivos")
            self.ui.print(f"  Salvo em: estrutura_projeto.json")
            
        except Exception as e:
            self.logger.warning(f"Falha ao analisar estrutura: {e}")
            self.ui.print("  Você pode executar manualmente: python locate/dds.py")
    
    def _force_scan_project(self) -> None:
        """Força análise completa da estrutura do projeto"""
        estrutura_path = os.path.join(self.project_root, "estrutura_projeto.json")
        
        # Remover arquivo antigo se existir
        if os.path.exists(estrutura_path):
            os.remove(estrutura_path)
            self.logger.info("Arquivo de estrutura anterior removido")
        
        # Executar análise
        self.ui.print(f"\n[bold]Analisando projeto:[/bold] {self.project_root}")
        self._analyze_project_structure(self.project_root)
    
    def _show_current_directory(self) -> None:
        """Mostrar diretório de trabalho atual"""
        from pathlib import Path
        
        self.ui.rule("Diretório de Trabalho")
        
        self.ui.print(f"\n[bold]Caminho:[/bold] {self.project_root}")
        
        # Verificar se existe estrutura_projeto.json
        estrutura_path = os.path.join(self.project_root, "estrutura_projeto.json")
        if os.path.exists(estrutura_path):
            import time
            import json
            
            file_age = time.time() - os.path.getmtime(estrutura_path)
            age_minutes = int(file_age / 60)
            
            try:
                with open(estrutura_path, 'r', encoding='utf-8') as f:
                    estrutura = json.load(f)
                
                self.ui.print(f"[bold]Estrutura analisada:[/bold] Sim (há {age_minutes} min)")
                self.ui.print(f"[bold]Arquivos catalogados:[/bold] {len(estrutura.get('estrutura', []))}")
            except:
                pass
        else:
            self.ui.print(f"[bold]Estrutura analisada:[/bold] Não (use /scan)")
        
        # Estatísticas do diretório
        try:
            python_files = list(Path(self.project_root).rglob('*.py'))
            subdirs = [d for d in Path(self.project_root).iterdir() if d.is_dir() and not d.name.startswith('.')]
            
            self.ui.print(f"[bold]Arquivos Python:[/bold] {len(python_files)}")
            self.ui.print(f"[bold]Subdiretórios:[/bold] {len(subdirs)}")
            
            if subdirs:
                self.ui.print(f"\n[bold]Principais diretórios:[/bold]")
                for subdir in sorted(subdirs)[:10]:
                    py_count = len(list(subdir.rglob('*.py')))
                    if py_count > 0:
                        self.ui.print(f"  {subdir.name}/ ({py_count} arquivos .py)")
        
        except Exception as e:
            self.logger.error(f"Erro ao analisar diretório: {e}")


def chat_loop():
    """Loop principal do chat"""
    ui = get_ui()
    logger = get_logger()
    
    # Carregar configuração
    try:
        config = ConfigManager()
        
        if not config.is_configured():
            logger.warning("Configuração necessária")
            config.interactive_setup()
    
    except Exception as e:
        logger.error(f"Erro de configuração: {e}")
        return
    
    project_root = os.path.dirname(__file__)
    
    # Inicializar assistente
    try:
        assistant = ChromaBuddyPro(config, project_root)
    except Exception as e:
        logger.error(f"Falha ao inicializar ChromaBuddy PRO: {e}")
        return
    
    # Exibir banner
    ui.clear()
    ui.rule("ChromaBuddy PRO - Assistente de Codificação com IA", style="bold cyan")
    
    ui.print("\n[bold]Recursos Principais:[/bold]")
    ui.print("  - Menções @ (como Cursor)")
    ui.print("  - Cache Inteligente (10x mais rápido)")
    ui.print("  - Análise de Dependências")
    ui.print("  - Diff Visual e Aprovação")
    ui.print("  - Análise de Qualidade de Código")
    ui.print("  - Geração Automática de Testes")
    ui.print("  - Auto-Correção (até 3 tentativas)")
    ui.print("  - Sistema de Aprendizado")
    
    ui.print("\n[bold]Recursos Avançados:[/bold]")
    ui.print("  - Integração Git")
    ui.print("  - Operações em Lote")
    ui.print("  - Gerador de Documentação")
    ui.print("  - Otimizador de Performance")
    ui.print("  - Ferramentas Inteligentes")
    ui.print("  - Sistema de Templates")
    ui.print("  - Modo Pensamento Profundo")
    
    ui.print("\nDigite [bold cyan]/help[/bold cyan] para ver comandos ou descreva o que você quer\n")
    
    # Loop principal
    while True:
        try:
            user_input = ui.prompt("\n>").strip()
            
            if not user_input or user_input.lower() in ['exit', 'quit', 'bye', 'sair']:
                logger.info("Encerrando...")
                assistant._show_stats()
                break
            
            assistant.process_command(user_input)
        
        except KeyboardInterrupt:
            logger.warning("\nInterrompido pelo usuário")
            break
        
        except Exception as e:
            logger.error(f"Erro: {e}")


if __name__ == "__main__":
    chat_loop()
