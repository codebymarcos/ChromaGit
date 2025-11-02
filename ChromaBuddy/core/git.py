# -*- coding: utf-8 -*-
import os
import subprocess
from datetime import datetime

class GitIntegration:
    def __init__(self, project_root):
        self.project_root = project_root
    
    def _run_git(self, command):
        try:
            result = subprocess.run(
                f"git {command}",
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            return result.stdout if result.returncode == 0 else result.stderr
        except:
            return None
    
    def status(self):
        output = self._run_git("status --short")
        if not output:
            return {'error': 'Git não disponível'}
        
        changes = {'modified': [], 'added': [], 'deleted': [], 'untracked': []}
        
        for line in output.strip().split('\n'):
            if not line:
                continue
            
            status = line[:2]
            filename = line[3:]
            
            if 'M' in status:
                changes['modified'].append(filename)
            elif 'A' in status:
                changes['added'].append(filename)
            elif 'D' in status:
                changes['deleted'].append(filename)
            elif '?' in status:
                changes['untracked'].append(filename)
        
        return changes
    
    def diff(self, filename=None):
        cmd = f"diff {filename}" if filename else "diff"
        return self._run_git(cmd)
    
    def commit(self, message, files=None):
        if files:
            for f in files:
                self._run_git(f"add {f}")
        else:
            self._run_git("add .")
        
        return self._run_git(f'commit -m "{message}"')
    
    def auto_commit(self, api_key, files_changed):
        # gerar mensagem de commit automática
        from models.cohe import generate
        
        changes = []
        for f in files_changed:
            diff = self.diff(f)
            if diff:
                changes.append(f"{f}:\n{diff[:200]}")
        
        sys_prompt = "Gere uma mensagem de commit git concisa e descritiva (máx 72 chars)."
        user_prompt = f"Mudanças:\n{chr(10).join(changes[:5])}"
        
        try:
            message = generate(api_key, sys_prompt, user_prompt).strip()
            # limpar
            message = message.replace('"', '').replace("'", "")[:72]
        except:
            message = f"Update: {len(files_changed)} files changed"
        
        return self.commit(message, files_changed)
    
    def create_branch(self, branch_name):
        return self._run_git(f"checkout -b {branch_name}")
    
    def switch_branch(self, branch_name):
        return self._run_git(f"checkout {branch_name}")
    
    def list_branches(self):
        output = self._run_git("branch -a")
        if output:
            return [b.strip().replace('*', '').strip() for b in output.split('\n') if b.strip()]
        return []
    
    def log(self, limit=10):
        output = self._run_git(f"log --oneline -n {limit}")
        if output:
            return output.strip().split('\n')
        return []
    
    def generate_pr_description(self, api_key):
        # gerar descrição de PR
        from models.cohe import generate
        
        diff = self.diff()
        log = self.log(5)
        
        sys_prompt = "Gere uma descrição profissional de Pull Request."
        user_prompt = f"""Commits recentes:
{chr(10).join(log)}

Diff (resumo):
{diff[:1000] if diff else 'Sem mudanças'}

Gere descrição com:
- Resumo das mudanças
- Por que foi feito
- Como testar"""
        
        try:
            return generate(api_key, sys_prompt, user_prompt).strip()
        except:
            return "Pull Request: Update code"
