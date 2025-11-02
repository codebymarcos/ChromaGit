# -*- coding: utf-8 -*-
import os
import json
import hashlib
import time
from pathlib import Path

class SmartCache:
    def __init__(self, cache_dir=".chromabuddy_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.memory = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def _hash(self, key):
        return hashlib.md5(str(key).encode()).hexdigest()
    
    def get(self, key, max_age=3600):
        # memoria
        if key in self.memory:
            self.hit_count += 1
            return self.memory[key]
        
        # disco
        cache_file = self.cache_dir / f"{self._hash(key)}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if time.time() - data['timestamp'] < max_age:
                    self.memory[key] = data['value']
                    self.hit_count += 1
                    return data['value']
            except:
                pass
        
        self.miss_count += 1
        return None
    
    def set(self, key, value, ttl=3600):
        self.memory[key] = value
        
        # salvar em disco
        cache_file = self.cache_dir / f"{self._hash(key)}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': time.time(),
                    'ttl': ttl,
                    'value': value
                }, f)
        except:
            pass
    
    def stats(self):
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0
        return {'hits': self.hit_count, 'misses': self.miss_count, 'rate': f"{hit_rate:.1f}%"}
    
    def clear(self):
        self.memory.clear()
        for f in self.cache_dir.glob("*.json"):
            f.unlink()

# singleton global
_cache = SmartCache()

def get_cache():
    return _cache
