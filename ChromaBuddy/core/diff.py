# -*- coding: utf-8 -*-
import difflib
from datetime import datetime

class DiffManager:
    def __init__(self):
        self.history = []
    
    def compare(self, original, modified, filename=""):
        diff = list(difflib.unified_diff(
            original.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile=f"{filename} (original)",
            tofile=f"{filename} (modificado)",
            lineterm=''
        ))
        
        return {
            'filename': filename,
            'diff': diff,
            'visual': self._format_visual(diff),
            'stats': self._stats(original, modified)
        }
    
    def _format_visual(self, diff):
        lines = []
        for line in diff:
            if line.startswith('+++') or line.startswith('---'):
                continue
            elif line.startswith('+'):
                lines.append(('add', line[1:]))
            elif line.startswith('-'):
                lines.append(('del', line[1:]))
            elif line.startswith('@@'):
                lines.append(('info', line))
            else:
                lines.append(('ctx', line))
        return lines
    
    def _stats(self, old, new):
        old_lines = old.count('\n') + 1
        new_lines = new.count('\n') + 1
        return {
            'old_lines': old_lines,
            'new_lines': new_lines,
            'delta': new_lines - old_lines
        }
    
    def save_snapshot(self, filepath, content):
        self.history.append({
            'filepath': filepath,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        if len(self.history) > 50:
            self.history.pop(0)
    
    def rollback(self, filepath, steps=1):
        matches = [h for h in reversed(self.history) if h['filepath'] == filepath]
        if len(matches) > steps:
            return matches[steps]['content']
        return None
    
    def interactive_approve(self, diff_result):
        approved_lines = []
        visual = diff_result['visual']
        
        print(f"\n{'='*60}")
        print(f"Arquivo: {diff_result['filename']}")
        print(f"Delta: {diff_result['stats']['delta']:+d} linhas")
        print(f"{'='*60}\n")
        
        i = 0
        while i < len(visual):
            typ, line = visual[i]
            
            if typ == 'add':
                print(f"  + {line.rstrip()}")
            elif typ == 'del':
                print(f"  - {line.rstrip()}")
            elif typ == 'info':
                print(f"\n{line}")
            else:
                print(f"    {line.rstrip()}")
            
            i += 1
        
        print(f"\n{'='*60}")
        choice = input("Aprovar mudanças? (s/n/p=parcial): ").strip().lower()
        
        return choice in ['s', 'sim', 'y', 'yes']
