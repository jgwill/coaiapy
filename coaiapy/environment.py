"""
Environment File Management for CoaiaPy

This module provides persistent environment variable management
for cross-session pipeline workflows.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, List, Any
from dataclasses import dataclass


@dataclass
class EnvironmentConfig:
    """Configuration for environment management"""
    project_env_file: str = ".coaia-env"
    global_env_file: str = "~/.coaia/global.env"
    supported_formats: List[str] = None
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ["json", "env"]


class EnvironmentManager:
    """Manages environment variables across sessions"""
    
    def __init__(self, config: Optional[EnvironmentConfig] = None):
        self.config = config or EnvironmentConfig()
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure necessary directories exist"""
        # Ensure global directory exists
        global_path = Path(self.config.global_env_file).expanduser()
        global_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_env_file_path(self, env_name: Optional[str] = None, 
                          location: str = "project") -> Path:
        """Get path to environment file"""
        if location == "global":
            base_path = Path(self.config.global_env_file).expanduser()
        else:
            base_path = Path.cwd() / self.config.project_env_file
        
        if env_name:
            # Add environment suffix (e.g., .coaia-env.dev)
            base_path = base_path.with_suffix(f"{base_path.suffix}.{env_name}")
        
        return base_path
    
    def _read_env_file(self, file_path: Path) -> Dict[str, Any]:
        """Read environment file (JSON or .env format)"""
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
                
            if not content:
                return {}
            
            # Try JSON first
            if content.startswith('{'):
                return json.loads(content)
            
            # Parse .env format
            env_vars = {}
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    env_vars[key.strip()] = value
            
            return env_vars
            
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return {}
    
    def _write_env_file(self, file_path: Path, env_vars: Dict[str, Any], 
                       format: str = "json"):
        """Write environment file"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            if format == "json":
                json.dump(env_vars, f, indent=2)
            else:  # .env format
                for key, value in env_vars.items():
                    # Quote values that contain spaces or special characters
                    if ' ' in str(value) or any(c in str(value) for c in '"\'$`'):
                        f.write(f'{key}="{value}"\n')
                    else:
                        f.write(f'{key}={value}\n')
    
    def list_environments(self) -> Dict[str, List[str]]:
        """List all available environment files"""
        environments = {"project": [], "global": []}
        
        # Check project environments
        project_dir = Path.cwd()
        base_env = self.config.project_env_file
        
        # Main environment file
        if (project_dir / base_env).exists():
            environments["project"].append("default")
        
        # Environment-specific files
        for env_file in project_dir.glob(f"{base_env}.*"):
            env_name = env_file.suffix[1:]  # Remove leading dot
            environments["project"].append(env_name)
        
        # Check global environments
        global_dir = Path(self.config.global_env_file).expanduser().parent
        base_global = Path(self.config.global_env_file).name
        
        if (global_dir / base_global).exists():
            environments["global"].append("default")
        
        for env_file in global_dir.glob(f"{base_global}.*"):
            env_name = env_file.suffix[1:]
            environments["global"].append(env_name)
        
        return environments
    
    def get_variable(self, key: str, env_name: Optional[str] = None,
                    location: str = "project") -> Optional[str]:
        """Get a specific environment variable"""
        env_vars = self.load_environment(env_name, location)
        return env_vars.get(key)
    
    def set_variable(self, key: str, value: Any, env_name: Optional[str] = None,
                    location: str = "project", persist: bool = True,
                    format: str = "json") -> Dict[str, Any]:
        """Set an environment variable"""
        if persist:
            # Load existing variables
            env_vars = self.load_environment(env_name, location)
            
            # Update variable
            env_vars[key] = value
            
            # Save back
            file_path = self._get_env_file_path(env_name, location)
            self._write_env_file(file_path, env_vars, format)
        else:
            # Just set in current environment
            os.environ[key] = str(value)
            env_vars = {key: value}
        
        return env_vars
    
    def unset_variable(self, key: str, env_name: Optional[str] = None,
                      location: str = "project", persist: bool = True,
                      format: str = "json") -> Dict[str, Any]:
        """Remove an environment variable"""
        if persist:
            # Load existing variables
            env_vars = self.load_environment(env_name, location)
            
            # Remove variable if it exists
            if key in env_vars:
                del env_vars[key]
            
            # Save back
            file_path = self._get_env_file_path(env_name, location)
            self._write_env_file(file_path, env_vars, format)
        else:
            # Just remove from current environment
            os.environ.pop(key, None)
            env_vars = {}
        
        return env_vars
    
    def load_environment(self, env_name: Optional[str] = None,
                        location: str = "project") -> Dict[str, Any]:
        """Load environment variables from file"""
        file_path = self._get_env_file_path(env_name, location)
        return self._read_env_file(file_path)
    
    def source_environment(self, env_name: Optional[str] = None,
                          location: str = "project") -> Dict[str, str]:
        """Load environment variables into current session"""
        env_vars = self.load_environment(env_name, location)
        
        # Set environment variables
        for key, value in env_vars.items():
            os.environ[key] = str(value)
        
        return env_vars
    
    def init_environment(self, env_name: Optional[str] = None,
                        location: str = "project", 
                        initial_vars: Optional[Dict[str, Any]] = None,
                        format: str = "json") -> Path:
        """Initialize a new environment file"""
        file_path = self._get_env_file_path(env_name, location)
        
        # Create initial variables
        env_vars = initial_vars or {
            "COAIA_TRACE_ID": "",
            "COAIA_SESSION_ID": "",
            "COAIA_USER_ID": "",
            "COAIA_LAST_OBSERVATION_ID": "",
            "COAIA_PARENT_OBSERVATION_ID": ""
        }
        
        # Add metadata
        import time
        env_vars["_COAIA_ENV_CREATED"] = str(int(time.time()))
        env_vars["_COAIA_ENV_NAME"] = env_name or "default"
        env_vars["_COAIA_ENV_LOCATION"] = location
        
        self._write_env_file(file_path, env_vars, format)
        return file_path
    
    def clear_environment(self, env_name: Optional[str] = None,
                         location: str = "project"):
        """Clear environment variables (remove file)"""
        file_path = self._get_env_file_path(env_name, location)
        if file_path.exists():
            file_path.unlink()
    
    def export_shell_commands(self, env_name: Optional[str] = None,
                             location: str = "project") -> List[str]:
        """Generate shell export commands"""
        env_vars = self.load_environment(env_name, location)
        
        commands = []
        for key, value in env_vars.items():
            if not key.startswith('_COAIA_ENV_'):  # Skip metadata
                # Escape quotes in value
                escaped_value = str(value).replace("'", "'\\''")
                commands.append(f"export {key}='{escaped_value}'")
        
        return commands
    
    def get_current_context(self) -> Dict[str, Optional[str]]:
        """Get current environment context from os.environ"""
        return {
            "COAIA_TRACE_ID": os.environ.get("COAIA_TRACE_ID"),
            "COAIA_SESSION_ID": os.environ.get("COAIA_SESSION_ID"),
            "COAIA_USER_ID": os.environ.get("COAIA_USER_ID"),
            "COAIA_LAST_OBSERVATION_ID": os.environ.get("COAIA_LAST_OBSERVATION_ID"),
            "COAIA_PARENT_OBSERVATION_ID": os.environ.get("COAIA_PARENT_OBSERVATION_ID")
        }
    
    def save_current_context(self, env_name: Optional[str] = None,
                           location: str = "project", 
                           name: Optional[str] = None) -> Path:
        """Save current environment context as a template"""
        current_context = self.get_current_context()
        
        # Filter out None values
        context_vars = {k: v for k, v in current_context.items() if v is not None}
        
        if name:
            context_vars["_COAIA_CONTEXT_NAME"] = name
        
        return self.init_environment(env_name, location, context_vars)


def format_environment_table(env_vars: Dict[str, Any]) -> str:
    """Format environment variables as a readable table"""
    if not env_vars:
        return "No environment variables set."
    
    # Filter out metadata for display
    display_vars = {k: v for k, v in env_vars.items() 
                   if not k.startswith('_COAIA_ENV_')}
    
    if not display_vars:
        return "No environment variables set."
    
    # Calculate column widths
    max_key = max([len(k) for k in display_vars.keys()] + [len('Variable')])
    max_value = max([len(str(v)[:50]) for v in display_vars.values()] + [len('Value')])
    
    # Build table
    separator = f"+{'-' * (max_key + 2)}+{'-' * (max_value + 2)}+"
    header = f"| {'Variable':<{max_key}} | {'Value':<{max_value}} |"
    
    lines = [separator, header, separator]
    
    for key, value in display_vars.items():
        # Truncate long values
        value_str = str(value)
        if len(value_str) > 50:
            value_str = value_str[:47] + "..."
        
        line = f"| {key:<{max_key}} | {value_str:<{max_value}} |"
        lines.append(line)
    
    lines.append(separator)
    lines.append(f"Total variables: {len(display_vars)}")
    
    return '\n'.join(lines)