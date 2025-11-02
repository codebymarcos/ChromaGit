# -*- coding: utf-8 -*-
"""
Configuration Manager for ChromaBuddy PRO
Handles user settings, API keys, and preferences
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration and user preferences"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to config file. Defaults to config.json in project root
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                    # Handle old format (list) vs new format (dict)
                    if isinstance(config_data, list) and len(config_data) > 0:
                        # Convert old format to new
                        return {
                            'api_key': config_data[0].get('api_key', ''),
                            'user_name': 'User',
                            'model': 'command-r-plus',
                            'max_tokens': 4000,
                            'temperature': 0.7,
                            'deep_think_enabled': False,
                            'deep_think_iterations': 3,
                            'cache_enabled': True,
                            'cache_ttl': 3600,
                            'auto_test': True,
                            'auto_fix_attempts': 3,
                            'diff_approval': True,
                            'theme': 'monokai'
                        }
                    return config_data
            else:
                # Create default config
                return self._create_default_config()
                
        except Exception as e:
            raise RuntimeError(f"Failed to load config: {e}")
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        default_config = {
            'api_key': '',
            'user_name': 'User',
            'model': 'command-r-plus',
            'max_tokens': 4000,
            'temperature': 0.7,
            'deep_think_enabled': False,
            'deep_think_iterations': 3,
            'cache_enabled': True,
            'cache_ttl': 3600,
            'auto_test': True,
            'auto_fix_attempts': 3,
            'diff_approval': True,
            'theme': 'monokai'
        }
        
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Save configuration to file
        
        Args:
            config: Configuration dict. If None, saves current config
        """
        if config is not None:
            self.config = config
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self.save_config()
    
    def get_api_key(self) -> str:
        """Get Cohere API key"""
        api_key = self.config.get('api_key', '')
        if not api_key:
            raise ValueError("API key not configured. Use /config to set it.")
        return api_key
    
    def set_api_key(self, api_key: str) -> None:
        """Set Cohere API key"""
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        self.set('api_key', api_key.strip())
    
    def get_user_name(self) -> str:
        """Get user name"""
        return self.config.get('user_name', 'User')
    
    def set_user_name(self, name: str) -> None:
        """Set user name"""
        if not name or not name.strip():
            raise ValueError("User name cannot be empty")
        self.set('user_name', name.strip())
    
    def is_configured(self) -> bool:
        """Check if essential configuration is present"""
        return bool(self.config.get('api_key'))
    
    def display_config(self) -> str:
        """Return formatted configuration for display"""
        lines = []
        lines.append("\nCurrent Configuration:")
        lines.append("-" * 50)
        
        # Mask API key
        api_key = self.config.get('api_key', '')
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "Not set"
        
        lines.append(f"API Key: {masked_key}")
        lines.append(f"User Name: {self.config.get('user_name', 'Not set')}")
        lines.append(f"Model: {self.config.get('model', 'Not set')}")
        lines.append(f"Max Tokens: {self.config.get('max_tokens', 'Not set')}")
        lines.append(f"Temperature: {self.config.get('temperature', 'Not set')}")
        lines.append(f"Deep Think: {'Enabled' if self.config.get('deep_think_enabled') else 'Disabled'}")
        lines.append(f"Cache: {'Enabled' if self.config.get('cache_enabled') else 'Disabled'}")
        lines.append(f"Auto Test: {'Enabled' if self.config.get('auto_test') else 'Disabled'}")
        lines.append(f"Diff Approval: {'Required' if self.config.get('diff_approval') else 'Auto-apply'}")
        lines.append(f"Theme: {self.config.get('theme', 'default')}")
        
        return '\n'.join(lines)
    
    def interactive_setup(self) -> None:
        """Interactive configuration setup"""
        print("\n" + "=" * 50)
        print("ChromaBuddy PRO - Configuration Setup")
        print("=" * 50)
        print("\nPress Enter to keep current value\n")
        
        # API Key
        current_key = self.config.get('api_key', '')
        masked = f"{current_key[:8]}...{current_key[-4:]}" if len(current_key) > 12 else "Not set"
        new_key = input(f"Cohere API Key [{masked}]: ").strip()
        if new_key:
            self.set_api_key(new_key)
        
        # User Name
        current_name = self.config.get('user_name', 'User')
        new_name = input(f"Your Name [{current_name}]: ").strip()
        if new_name:
            self.set_user_name(new_name)
        
        # Model
        current_model = self.config.get('model', 'command-r-plus')
        print(f"\nAvailable models:")
        print("  1. command-r-plus (recommended)")
        print("  2. command-r")
        print("  3. command")
        model_choice = input(f"Model [{current_model}]: ").strip()
        if model_choice == '1':
            self.set('model', 'command-r-plus')
        elif model_choice == '2':
            self.set('model', 'command-r')
        elif model_choice == '3':
            self.set('model', 'command')
        elif model_choice:
            self.set('model', model_choice)
        
        # Deep Think
        current_deep = self.config.get('deep_think_enabled', False)
        deep_choice = input(f"Enable Deep Think Mode? (y/n) [{'y' if current_deep else 'n'}]: ").strip().lower()
        if deep_choice == 'y':
            self.set('deep_think_enabled', True)
        elif deep_choice == 'n':
            self.set('deep_think_enabled', False)
        
        # Temperature
        current_temp = self.config.get('temperature', 0.7)
        temp_input = input(f"Temperature (0.0-1.0) [{current_temp}]: ").strip()
        if temp_input:
            try:
                temp = float(temp_input)
                if 0.0 <= temp <= 1.0:
                    self.set('temperature', temp)
                else:
                    print("Temperature must be between 0.0 and 1.0")
            except ValueError:
                print("Invalid temperature value")
        
        print("\nConfiguration saved successfully!")
        print(self.display_config())
