"""
Mobile Template Engine for CoaiaPy

Pure-Python template engine optimized for Pythonista and mobile environments.
Replaces Jinja2 dependency with lightweight, build-free template processing.
"""

import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union


class MobileTemplateEngine:
    """Lightweight templating designed for Pythonista workflows"""
    
    def __init__(self):
        # Built-in functions for mobile workflows
        self.builtin_functions = {
            'uuid4': lambda: str(uuid.uuid4()),
            'now': lambda: datetime.utcnow().isoformat() + 'Z',
            'timestamp': lambda: datetime.utcnow().isoformat() + 'Z',
            'mobile_id': lambda: f"mobile_{str(uuid.uuid4())[:8]}",  # Short IDs for mobile
            'touch_timestamp': lambda: datetime.now().strftime("%H:%M:%S")  # Local time for mobile UX
        }
        
        # Patterns for template processing
        self.variable_pattern = re.compile(r'\{\{([^}]+)\}\}')
        self.condition_pattern = re.compile(r'\{\%\s*if\s+([^%]+)\%\}(.*?)\{\%\s*endif\s*\%\}', re.DOTALL)
    
    def render_pipeline(self, template_name: str, **variables) -> Dict[str, Any]:
        """Fast, mobile-optimized template processing"""
        # This would typically load from a template registry
        # For now, we'll integrate with the existing template system
        return self.render_template_content("", variables)
    
    def render_template_content(self, content: str, variables: Dict[str, Any]) -> str:
        """Render template content with variable substitution and conditionals"""
        if not content:
            return ""
        
        # First, process conditionals
        result = self._process_conditionals(content, variables)
        
        # Then, process variable substitutions
        result = self._process_variables(result, variables)
        
        return result
    
    def render_string(self, text: str, variables: Dict[str, Any]) -> str:
        """Render a string template with variables - API compatible with Jinja2"""
        return self.render_template_content(text, variables)
    
    def render_dict(self, data: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively render dictionary values"""
        if not isinstance(data, dict):
            return data
        
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.render_string(value, variables)
            elif isinstance(value, dict):
                result[key] = self.render_dict(value, variables)
            elif isinstance(value, list):
                result[key] = self.render_list(value, variables)
            else:
                result[key] = value
        
        return result
    
    def render_list(self, data: List[Any], variables: Dict[str, Any]) -> List[Any]:
        """Recursively render list values"""
        if not isinstance(data, list):
            return data
        
        result = []
        for item in data:
            if isinstance(item, str):
                result.append(self.render_string(item, variables))
            elif isinstance(item, dict):
                result.append(self.render_dict(item, variables))
            elif isinstance(item, list):
                result.append(self.render_list(item, variables))
            else:
                result.append(item)
        
        return result
    
    def _process_variables(self, content: str, variables: Dict[str, Any]) -> str:
        """Process {{variable}} substitutions with mobile-friendly fallbacks"""
        def replace_variable(match):
            var_expr = match.group(1).strip()
            
            # Handle function calls like uuid4()
            if var_expr.endswith('()') and var_expr[:-2] in self.builtin_functions:
                func_name = var_expr[:-2]
                return str(self.builtin_functions[func_name]())
            
            # Handle filters like variable|title, variable|upper
            if '|' in var_expr:
                parts = var_expr.split('|')
                var_name = parts[0].strip()
                filter_name = parts[1].strip()
                
                if var_name in variables:
                    value = str(variables[var_name]) if variables[var_name] is not None else ''
                    return self._apply_filter(value, filter_name)
                else:
                    return f"[{var_name}]"  # Missing variable
            
            # Handle 'variable or default' expressions
            if ' or ' in var_expr:
                parts = [p.strip().strip("'\"") for p in var_expr.split(' or ')]
                for part in parts:
                    if part in variables and variables[part] is not None:
                        return str(variables[part])
                    elif part.startswith("'") and part.endswith("'"):
                        return part[1:-1]  # Return string literal
                    elif part.startswith('"') and part.endswith('"'):
                        return part[1:-1]  # Return string literal
                return parts[-1]  # Return last part as fallback
            
            # Simple variable lookup
            if var_expr in variables:
                value = variables[var_expr]
                return str(value) if value is not None else ''
            
            # Mobile-friendly fallback for missing variables
            return f"[{var_expr}]"  # Clear indication of missing variable
        
        return self.variable_pattern.sub(replace_variable, content)
    
    def _apply_filter(self, value: str, filter_name: str) -> str:
        """Apply mobile-friendly filters to values"""
        if filter_name == 'title':
            return value.title()
        elif filter_name == 'upper':
            return value.upper()
        elif filter_name == 'lower':
            return value.lower()
        elif filter_name == 'capitalize':
            return value.capitalize()
        elif filter_name == 'strip':
            return value.strip()
        else:
            # For unknown filters, return original value
            return value
    
    def _process_conditionals(self, content: str, variables: Dict[str, Any]) -> str:
        """Process {% if condition %}...{% endif %} blocks"""
        def replace_condition(match):
            condition_expr = match.group(1).strip()
            conditional_content = match.group(2)
            
            # Simple condition evaluation
            if self._evaluate_condition(condition_expr, variables):
                return conditional_content
            else:
                return ""
        
        return self.condition_pattern.sub(replace_condition, content)
    
    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """Simple condition evaluation for mobile templates"""
        condition = condition.strip()
        
        # Handle 'not variable' conditions
        if condition.startswith('not '):
            var_name = condition[4:].strip()
            return not self._is_truthy(variables.get(var_name))
        
        # Handle simple variable existence checks
        if condition in variables:
            return self._is_truthy(variables[condition])
        
        # Handle 'variable == "value"' comparisons
        if '==' in condition:
            left, right = [p.strip() for p in condition.split('==', 1)]
            left_val = variables.get(left, left.strip("'\""))
            right_val = right.strip("'\"")
            return str(left_val) == right_val
        
        # Handle 'variable != "value"' comparisons  
        if '!=' in condition:
            left, right = [p.strip() for p in condition.split('!=', 1)]
            left_val = variables.get(left, left.strip("'\""))
            right_val = right.strip("'\"")
            return str(left_val) != right_val
        
        # Default to False for unknown conditions
        return False
    
    def _is_truthy(self, value: Any) -> bool:
        """Mobile-friendly truthiness evaluation"""
        if value is None or value == "" or value == []:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value.lower() not in ('false', '0', 'no', 'off', 'disabled')
        return bool(value)


class MobileEnvironment:
    """Compatibility layer for Jinja2 Environment API"""
    
    def __init__(self, loader=None):
        self.engine = MobileTemplateEngine()
        # Add built-in globals for API compatibility
        self.globals = {
            'uuid4': self.engine.builtin_functions['uuid4'],
            'now': self.engine.builtin_functions['now'],
            'timestamp': self.engine.builtin_functions['timestamp']
        }
    
    def from_string(self, template_string: str):
        """Create a template from string - Jinja2 API compatibility"""
        return MobileTemplate(template_string, self.engine)


class MobileTemplate:
    """Template object for API compatibility with Jinja2"""
    
    def __init__(self, template_string: str, engine: MobileTemplateEngine):
        self.template_string = template_string
        self.engine = engine
    
    def render(self, **kwargs) -> str:
        """Render template with variables - Jinja2 API compatibility"""
        return self.engine.render_template_content(self.template_string, kwargs)