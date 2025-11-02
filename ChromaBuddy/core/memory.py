# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
from pathlib import Path

class MemorySystem:
    def __init__(self, memory_file=".chromabuddy_memory.json"):
        self.memory_file = Path(memory_file)
        self.data = self._load()
    
    def _load(self):
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'interactions': [],
            'patterns': {},
            'preferences': {},
            'frequent_files': {},
            'common_tasks': []
        }
    
    def _save(self):
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def record_interaction(self, user_input, files_modified, success=True):
        self.data['interactions'].append({
            'timestamp': datetime.now().isoformat(),
            'input': user_input,
            'files': files_modified,
            'success': success
        })
        
        # limitar historico
        if len(self.data['interactions']) > 100:
            self.data['interactions'] = self.data['interactions'][-100:]
        
        # atualizar frequencia de arquivos
        for f in files_modified:
            self.data['frequent_files'][f] = self.data['frequent_files'].get(f, 0) + 1
        
        self._save()
    
    def learn_pattern(self, pattern_name, context):
        if pattern_name not in self.data['patterns']:
            self.data['patterns'][pattern_name] = []
        
        self.data['patterns'][pattern_name].append({
            'timestamp': datetime.now().isoformat(),
            'context': context
        })
        
        if len(self.data['patterns'][pattern_name]) > 20:
            self.data['patterns'][pattern_name] = self.data['patterns'][pattern_name][-20:]
        
        self._save()
    
    def get_pattern_suggestions(self, current_context):
        suggestions = []
        
        for pattern_name, instances in self.data['patterns'].items():
            if len(instances) >= 3:
                suggestions.append({
                    'pattern': pattern_name,
                    'frequency': len(instances),
                    'recent': instances[-1]['timestamp']
                })
        
        return sorted(suggestions, key=lambda x: x['frequency'], reverse=True)
    
    def get_frequent_files(self, limit=10):
        return sorted(
            self.data['frequent_files'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
    
    def set_preference(self, key, value):
        self.data['preferences'][key] = value
        self._save()
    
    def get_preference(self, key, default=None):
        return self.data['preferences'].get(key, default)
    
    def suggest_next_action(self):
        recent = self.data['interactions'][-5:]
        if not recent:
            return None
        
        # analisar padroes recentes
        files = set()
        for interaction in recent:
            files.update(interaction.get('files', []))
        
        if files:
            return f"Arquivos trabalhados recentemente: {', '.join(list(files)[:3])}"
        
        return None
    
    def get_stats(self):
        total_interactions = len(self.data['interactions'])
        success_rate = 0
        
        if total_interactions > 0:
            successes = sum(1 for i in self.data['interactions'] if i.get('success'))
            success_rate = (successes / total_interactions) * 100
        
        return {
            'total_interactions': total_interactions,
            'success_rate': f"{success_rate:.1f}%",
            'patterns_learned': len(self.data['patterns']),
            'files_tracked': len(self.data['frequent_files'])
        }
