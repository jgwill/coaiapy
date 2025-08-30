"""
Pipeline Template Management for CoaiaPy

This module provides template-based pipeline creation and management
for Langfuse observability workflows.
"""

import os
import json
import yaml
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import re
from .mobile_template import MobileTemplateEngine, MobileEnvironment, MobileTemplate


@dataclass
class PipelineVariable:
    """Represents a variable in a pipeline template"""
    name: str
    type: str = "string"  # string, number, boolean, list
    required: bool = True
    default: Optional[Any] = None
    description: Optional[str] = None
    choices: Optional[List[Any]] = None  # For enum-like variables


@dataclass 
class PipelineStep:
    """Represents a single step in a pipeline template"""
    name: str
    observation_type: str = "EVENT"  # EVENT, SPAN, GENERATION
    description: Optional[str] = None
    parent: Optional[str] = None  # Name of parent step
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    conditional: Optional[str] = None  # Jinja2 condition for inclusion
    

@dataclass
class PipelineTemplate:
    """Represents a complete pipeline template"""
    name: str
    version: str = "1.0"
    description: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[str] = None
    variables: List[PipelineVariable] = field(default_factory=list)
    steps: List[PipelineStep] = field(default_factory=list)
    extends: Optional[str] = None  # Name of base template to inherit from
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_variable_names(self) -> List[str]:
        """Get list of all variable names defined in template"""
        return [var.name for var in self.variables]
    
    def get_required_variables(self) -> List[str]:
        """Get list of required variable names"""
        return [var.name for var in self.variables if var.required and var.default is None]
    
    def validate_variables(self, provided_vars: Dict[str, Any]) -> List[str]:
        """Validate provided variables against template requirements"""
        errors = []
        
        # Check required variables
        for req_var in self.get_required_variables():
            if req_var not in provided_vars:
                errors.append(f"Required variable '{req_var}' not provided")
        
        # Check variable types and choices
        for var in self.variables:
            if var.name in provided_vars:
                value = provided_vars[var.name]
                
                # Type validation
                if var.type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"Variable '{var.name}' must be a number")
                elif var.type == "boolean" and not isinstance(value, bool):
                    errors.append(f"Variable '{var.name}' must be a boolean")
                elif var.type == "list" and not isinstance(value, list):
                    errors.append(f"Variable '{var.name}' must be a list")
                
                # Choice validation
                if var.choices and value not in var.choices:
                    errors.append(f"Variable '{var.name}' must be one of: {var.choices}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for JSON/YAML serialization"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "created_at": self.created_at,
            "extends": self.extends,
            "metadata": self.metadata,
            "variables": [
                {
                    "name": var.name,
                    "type": var.type,
                    "required": var.required,
                    "default": var.default,
                    "description": var.description,
                    "choices": var.choices
                }
                for var in self.variables
            ],
            "steps": [
                {
                    "name": step.name,
                    "observation_type": step.observation_type,
                    "description": step.description,
                    "parent": step.parent,
                    "variables": step.variables,
                    "metadata": step.metadata,
                    "conditional": step.conditional
                }
                for step in self.steps
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineTemplate':
        """Create template from dictionary (JSON/YAML)"""
        variables = [
            PipelineVariable(
                name=var_data["name"],
                type=var_data.get("type", "string"),
                required=var_data.get("required", True),
                default=var_data.get("default"),
                description=var_data.get("description"),
                choices=var_data.get("choices")
            )
            for var_data in data.get("variables", [])
        ]
        
        steps = [
            PipelineStep(
                name=step_data["name"],
                observation_type=step_data.get("observation_type", "EVENT"),
                description=step_data.get("description"),
                parent=step_data.get("parent"),
                variables=step_data.get("variables", {}),
                metadata=step_data.get("metadata", {}),
                conditional=step_data.get("conditional")
            )
            for step_data in data.get("steps", [])
        ]
        
        return cls(
            name=data["name"],
            version=data.get("version", "1.0"),
            description=data.get("description"),
            author=data.get("author"),
            created_at=data.get("created_at"),
            extends=data.get("extends"),
            metadata=data.get("metadata", {}),
            variables=variables,
            steps=steps
        )


class TemplateLoader:
    """Handles loading and discovery of pipeline templates"""
    
    def __init__(self):
        self.search_paths = self._get_search_paths()
    
    def _get_search_paths(self) -> List[Path]:
        """Get template search paths in priority order"""
        paths = []
        
        # 1. Project templates (highest priority)
        project_path = Path.cwd() / ".coaia" / "templates"
        if project_path.exists():
            paths.append(project_path)
        
        # 2. User global templates
        user_path = Path.home() / ".coaia" / "templates"
        if user_path.exists():
            paths.append(user_path)
        
        # 3. Built-in templates (lowest priority)
        builtin_path = Path(__file__).parent / "templates"
        if builtin_path.exists():
            paths.append(builtin_path)
        
        return paths
    
    def list_templates(self, include_path: bool = False) -> List[Dict[str, Any]]:
        """List all available templates"""
        templates = []
        seen_names = set()
        
        for search_path in self.search_paths:
            for template_file in search_path.glob("*.json"):
                try:
                    template = self.load_template(template_file.stem)
                    if template and template.name not in seen_names:
                        template_info = {
                            "name": template.name,
                            "description": template.description,
                            "version": template.version,
                            "author": template.author
                        }
                        if include_path:
                            template_info["path"] = str(template_file)
                        templates.append(template_info)
                        seen_names.add(template.name)
                except Exception:
                    continue  # Skip invalid templates
        
        # Also check YAML files
        for search_path in self.search_paths:
            for template_file in search_path.glob("*.yaml"):
                try:
                    template = self.load_template(template_file.stem)
                    if template and template.name not in seen_names:
                        template_info = {
                            "name": template.name,
                            "description": template.description,
                            "version": template.version,
                            "author": template.author
                        }
                        if include_path:
                            template_info["path"] = str(template_file)
                        templates.append(template_info)
                        seen_names.add(template.name)
                except Exception:
                    continue
        
        return templates
    
    def load_template(self, name: str) -> Optional[PipelineTemplate]:
        """Load a template by name, searching all paths"""
        for search_path in self.search_paths:
            # Try JSON first
            json_file = search_path / f"{name}.json"
            if json_file.exists():
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    return PipelineTemplate.from_dict(data)
                except Exception:
                    continue
            
            # Try YAML
            yaml_file = search_path / f"{name}.yaml"
            if yaml_file.exists():
                try:
                    with open(yaml_file, 'r') as f:
                        data = yaml.safe_load(f)
                    return PipelineTemplate.from_dict(data)
                except Exception:
                    continue
        
        return None
    
    def save_template(self, template: PipelineTemplate, 
                     location: str = "user",  # "user" or "project"
                     format: str = "json") -> Path:
        """Save a template to specified location"""
        if location == "project":
            save_path = Path.cwd() / ".coaia" / "templates"
        else:  # user
            save_path = Path.home() / ".coaia" / "templates"
        
        # Create directory if it doesn't exist
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Determine filename
        extension = ".json" if format == "json" else ".yaml"
        filename = save_path / f"{template.name}{extension}"
        
        # Save template
        template_dict = template.to_dict()
        if not template_dict.get("created_at"):
            template_dict["created_at"] = datetime.utcnow().isoformat() + 'Z'
        
        with open(filename, 'w') as f:
            if format == "json":
                json.dump(template_dict, f, indent=2)
            else:
                yaml.safe_dump(template_dict, f, default_flow_style=False)
        
        return filename


class TemplateRenderer:
    """Handles variable substitution and template rendering"""
    
    def __init__(self):
        self.env = MobileEnvironment()
        # Built-in functions are automatically available in MobileEnvironment
    
    def render_template(self, template: PipelineTemplate, 
                       variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Render template with provided variables to create observations"""
        # Validate variables first
        errors = template.validate_variables(variables)
        if errors:
            raise ValueError(f"Template validation failed: {'; '.join(errors)}")
        
        # Merge with defaults
        final_vars = {}
        for var in template.variables:
            if var.name in variables:
                final_vars[var.name] = variables[var.name]
            elif var.default is not None:
                final_vars[var.name] = var.default
        
        observations = []
        
        for step in template.steps:
            # Check conditional
            if step.conditional:
                condition_template = self.env.from_string(step.conditional)
                if not condition_template.render(**final_vars):
                    continue  # Skip this step
            
            # Render step variables
            rendered_step = {
                "name": self._render_string(step.name, final_vars),
                "type": step.observation_type,
                "description": self._render_string(step.description or "", final_vars),
                "variables": self._render_dict(step.variables, final_vars),
                "metadata": self._render_dict(step.metadata, final_vars)
            }
            
            # Handle parent reference
            if step.parent:
                rendered_step["parent"] = self._render_string(step.parent, final_vars)
            
            observations.append(rendered_step)
        
        return observations
    
    def _render_string(self, text: str, variables: Dict[str, Any]) -> str:
        """Render a string template with variables"""
        if not text:
            return ""
        template = self.env.from_string(text)
        return template.render(**variables)
    
    def _render_dict(self, data: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively render dictionary values"""
        if not data:
            return {}
        
        # Use mobile template engine's built-in dict rendering
        return self.env.engine.render_dict(data, variables)
    
    def render_with_judge_integration(self, template: PipelineTemplate, 
                                    variables: Dict[str, Any],
                                    enable_judge_calls: bool = False) -> List[Dict[str, Any]]:
        """Render template with optional LLM-as-a-Judge API integration"""
        # First render normally
        observations = self.render_template(template, variables)
        
        # If judge integration is enabled, process judge steps
        if enable_judge_calls:
            observations = self._process_judge_steps(observations, variables)
        
        return observations
    
    def _process_judge_steps(self, observations: List[Dict[str, Any]], 
                           variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process steps that require LLM-as-a-Judge API calls"""
        processed_observations = []
        
        for obs in observations:
            # Check if this is a judge evaluation step
            if self._is_judge_step(obs):
                # TODO: Integrate with actual LLM-as-a-Judge API when available
                # For now, enhance the observation with judge integration metadata
                obs = self._prepare_judge_step(obs, variables)
            
            processed_observations.append(obs)
        
        return processed_observations
    
    def _is_judge_step(self, observation: Dict[str, Any]) -> bool:
        """Check if an observation represents a judge evaluation step"""
        step_name = observation.get('name', '').lower()
        description = observation.get('description', '').lower()
        metadata = observation.get('metadata', {})
        
        # Look for judge indicators
        judge_indicators = ['judge', 'evaluation', 'assess', 'scoring', 'rating']
        
        return (
            any(indicator in step_name for indicator in judge_indicators) or
            any(indicator in description for indicator in judge_indicators) or
            'judge_model' in metadata or
            'evaluation_criteria' in metadata
        )
    
    def _prepare_judge_step(self, observation: Dict[str, Any], 
                           variables: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare observation for LLM-as-a-Judge integration"""
        # Add judge integration metadata
        if 'metadata' not in observation:
            observation['metadata'] = {}
        
        observation['metadata']['judge_integration_ready'] = True
        observation['metadata']['judge_api_placeholder'] = True
        
        # Extract judge parameters if available
        metadata = observation.get('metadata', {})
        judge_params = {}
        
        if 'judge_model' in metadata:
            judge_params['model'] = metadata['judge_model']
        if 'evaluation_criteria' in metadata:
            judge_params['criteria'] = metadata['evaluation_criteria']
        
        # Add judge parameters to variables
        if judge_params:
            if 'variables' not in observation:
                observation['variables'] = {}
            if 'input' not in observation['variables']:
                observation['variables']['input'] = {}
            
            observation['variables']['input']['judge_params'] = judge_params
            
            # TODO: When LLM-as-a-Judge API is available, this is where we would:
            # 1. Extract content to evaluate from observation
            # 2. Call LLM-as-a-Judge API with judge_params 
            # 3. Update observation output with actual judge results
            # 4. Store judge reasoning and scores
            # 
            # Example future integration:
            # from cofuse import llm_judge_evaluate
            # judge_result = llm_judge_evaluate(
            #     content=observation['variables']['input'].get('content'),
            #     model=judge_params.get('model', 'gpt-4'),
            #     criteria=judge_params.get('criteria', 'helpfulness')
            # )
            # observation['variables']['output']['judge_score'] = judge_result['score']
            # observation['variables']['output']['judge_reasoning'] = judge_result['reasoning']
        
        return observation