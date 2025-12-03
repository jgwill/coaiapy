"""
MCP Server feature configuration.

Allows selective exposure of tools/prompts/resources via COAIAPY_MCP_FEATURES
environment variable to reduce token usage in Claude Code context.

Feature Sets:
- MINIMAL: Core observability (traces, observations, comments, prompts, datasets, scores)
- STANDARD: MINIMAL + workflow prompts + resources [DEFAULT]
- OBSERVABILITY: Same as STANDARD (reserved for future expansion)
- FULL: Everything including Mia & Miette persona prompts and media tools
"""

import os
from typing import Set, Dict, List

# ============================================================================
# Feature Set Definitions
# ============================================================================

# All available tools
ALL_TOOLS = {
    # Redis
    "coaia_tash",
    "coaia_fetch",
    # Trace creation and management
    "coaia_fuse_trace_create",
    "coaia_fuse_add_observation",
    "coaia_fuse_trace_patch_output",
    "coaia_fuse_trace_get",
    "coaia_fuse_trace_view",
    "coaia_fuse_observation_get",
    "coaia_fuse_traces_session_view",
    # Comments
    "coaia_fuse_comments_list",
    "coaia_fuse_comments_get",
    "coaia_fuse_comments_create",
    # Prompts
    "coaia_fuse_prompts_list",
    "coaia_fuse_prompts_get",
    # Datasets
    "coaia_fuse_datasets_list",
    "coaia_fuse_datasets_get",
    # Score configs
    "coaia_fuse_score_configs_list",
    "coaia_fuse_score_configs_get",
    # Media (FULL only)
    "coaia_fuse_media_upload",
    "coaia_fuse_media_get",
}

# Core tools available in MINIMAL
MINIMAL_TOOLS = {
    # Redis
    "coaia_tash",
    "coaia_fetch",
    # Trace creation and management
    "coaia_fuse_trace_create",
    "coaia_fuse_add_observation",
    "coaia_fuse_trace_patch_output",
    "coaia_fuse_trace_get",
    "coaia_fuse_trace_view",
    "coaia_fuse_observation_get",
    "coaia_fuse_traces_session_view",
    # Comments
    "coaia_fuse_comments_list",
    "coaia_fuse_comments_get",
    "coaia_fuse_comments_create",
    # Prompts
    "coaia_fuse_prompts_list",
    "coaia_fuse_prompts_get",
    # Datasets
    "coaia_fuse_datasets_list",
    "coaia_fuse_datasets_get",
    # Score configs
    "coaia_fuse_score_configs_list",
    "coaia_fuse_score_configs_get",
}

# Media tools (FULL only)
MEDIA_TOOLS = {
    "coaia_fuse_media_upload",
    "coaia_fuse_media_get",
}

# All available prompts
ALL_PROMPTS = {
    "mia_miette_duo",
    "create_observability_pipeline",
    "analyze_audio_workflow",
}

# Workflow prompts (STANDARD and above)
WORKFLOW_PROMPTS = {
    "create_observability_pipeline",
    "analyze_audio_workflow",
}

# Persona prompts (FULL only)
PERSONA_PROMPTS = {
    "mia_miette_duo",
}

# All available resources
ALL_RESOURCES = {
    "coaia://templates/",
}

# Feature set mappings
FEATURE_SETS: Dict[str, Dict[str, Set[str]]] = {
    "MINIMAL": {
        "tools": MINIMAL_TOOLS,
        "prompts": set(),
        "resources": set(),
    },
    "STANDARD": {
        "tools": MINIMAL_TOOLS,
        "prompts": WORKFLOW_PROMPTS,
        "resources": ALL_RESOURCES,
    },
    "OBSERVABILITY": {
        "tools": MINIMAL_TOOLS,
        "prompts": WORKFLOW_PROMPTS,
        "resources": ALL_RESOURCES,
    },
    "FULL": {
        "tools": ALL_TOOLS,
        "prompts": ALL_PROMPTS,
        "resources": ALL_RESOURCES,
    },
}


# ============================================================================
# Configuration Loading
# ============================================================================

class FeatureConfig:
    """
    Feature configuration manager.

    Reads COAIAPY_MCP_FEATURES environment variable and provides
    methods to check if specific features are enabled.
    """

    def __init__(self):
        self.feature_level = os.getenv("COAIAPY_MCP_FEATURES", "STANDARD").upper()

        if self.feature_level not in FEATURE_SETS:
            print(f"⚠️  Invalid COAIAPY_MCP_FEATURES='{self.feature_level}', using STANDARD")
            self.feature_level = "STANDARD"

        self.config = FEATURE_SETS[self.feature_level]

    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool is enabled in current feature set."""
        return tool_name in self.config["tools"]

    def is_prompt_enabled(self, prompt_id: str) -> bool:
        """Check if a prompt is enabled in current feature set."""
        return prompt_id in self.config["prompts"]

    def is_resource_enabled(self, resource_uri: str) -> bool:
        """Check if a resource is enabled in current feature set."""
        # Check if any enabled resource pattern matches
        for enabled_uri in self.config["resources"]:
            if resource_uri.startswith(enabled_uri.rstrip("/")):
                return True
        return False

    def get_enabled_tools(self) -> Set[str]:
        """Get set of enabled tool names."""
        return self.config["tools"]

    def get_enabled_prompts(self) -> Set[str]:
        """Get set of enabled prompt IDs."""
        return self.config["prompts"]

    def get_enabled_resources(self) -> Set[str]:
        """Get set of enabled resource URIs."""
        return self.config["resources"]

    def get_feature_level(self) -> str:
        """Get current feature level."""
        return self.feature_level

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about enabled features."""
        return {
            "tools": len(self.config["tools"]),
            "prompts": len(self.config["prompts"]),
            "resources": len(self.config["resources"]),
            "level": self.feature_level,
        }


# Global configuration instance
config = FeatureConfig()


def get_config() -> FeatureConfig:
    """Get the global feature configuration."""
    return config


__all__ = [
    "FeatureConfig",
    "get_config",
    "FEATURE_SETS",
    "ALL_TOOLS",
    "ALL_PROMPTS",
    "ALL_RESOURCES",
]
