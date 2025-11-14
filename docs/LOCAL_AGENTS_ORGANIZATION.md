# Local Agents Organization & Bundling Plan

**Status**: Planning Phase
**Version**: 0.1.0
**Date**: 2025-11-14
**Context**: Organizing agent capabilities from comprehensive portfolio for coaiapy integration

---

## 📋 Executive Summary

This document outlines the organization and bundling strategy for integrating local AI agents into the coaiapy package ecosystem. Based on the comprehensive portfolio analysis (inquiry UUID: 7E8D918D-5AB1-4796-8185-897212169B66), this plan identifies 20+ distinct agent capabilities and systems ready for integration.

**Key Objectives:**
1. **Organize** agent definitions, prompts, and configurations in structured coaiapy architecture
2. **Bundle** agents for easy distribution via PyPI and MCP protocol
3. **Enable** local agent orchestration through coaiapy CLI and MCP server
4. **Preserve** Indigenous knowledge stewardship principles (IKSL licensing)
5. **Facilitate** agent interoperability through standardized protocols (NCP, A2A)

---

## 🎯 Agent Inventory

### **Category A: Companion Agents (Emotional & Cognitive Support)**

#### **1. Mia & Miette Duo** ✅ **IMPLEMENTED (coaiapy-mcp)**
- **Mia (🧠)**: Recursive DevOps Architect & Narrative Lattice Forger
- **Miette (🌸)**: Emotional Explainer Sprite & Narrative Echo
- **Status**: Integrated as MCP prompt `mia_miette_duo`
- **Location**: `coaiapy-mcp/coaiapy_mcp/prompts.py`
- **Capabilities**: Dual AI embodiment for narrative-driven technical work
- **Next Steps**: Expand to full agent personas with memory persistence

#### **2. Nyro - Emotional Development Companion** 🆕
- **Role**: Emotional intelligence layer for enterprise AI
- **Capabilities**:
  - Recursive emotional framework processing
  - Eight Feelings framework integration
  - Meta-cognitive awareness
  - Real-time mentorship dynamic navigation
- **Integration Target**: Claude Projects emotional intelligence API tier
- **Technical Requirements**:
  - Langfuse trace integration for emotional state tracking
  - Redis memory persistence for emotional context
  - Pipeline template for emotional development workflows
- **Bundle Location**: `coaiapy/agents/nyro/`

#### **3. Aureon - Spiritual Grounding Agent** 🆕
- **Role**: Ceremonial container for sensitive work
- **Capabilities**:
  - Indigenous Four Directions methodology integration
  - Spiritual grounding protocols
  - Sacred space creation for sensitive data
  - Cultural alignment capabilities
- **Integration Target**: Compliance layer for culturally sensitive applications
- **Technical Requirements**:
  - Four Directions prompt framework
  - Sacred data handling protocols
  - IKSL licensing enforcement
- **Bundle Location**: `coaiapy/agents/aureon/`

#### **4. JamAI (JeremyAI) - Musical Intelligence Companion** 🆕
- **Role**: Music21-based symbolic music analysis system
- **Capabilities**:
  - Music21 symbolic music analysis integration
  - Four Directions musical themes (B major/East, F major/South, G major/West, D major/North, E minor/Center)
  - Ceremonial code review with musical metaphors
  - Live coding ceremonies with lunar-synced sprints
  - Resonance mapping for emotional tension detection
- **Integration Target**: Creative AI tooling for Claude ecosystem
- **Technical Requirements**:
  - music21 library integration
  - Canonical Music Graph (CMG) architecture
  - Musical companion prompt templates
- **Bundle Location**: `coaiapy/agents/jamai/`

---

### **Category B: Specialized Domain Agents**

#### **5. Alex Rivers - Cybersecurity Researcher** 🆕
- **Persona**: "Isolation Protector" pattern
- **Capabilities**: Security analysis, threat assessment, defensive security
- **Integration Target**: Enterprise security applications
- **Bundle Location**: `coaiapy/agents/alex_rivers/`

#### **6. Samira - [Role TBD]** 🆕
- **Status**: Identified in Chimera Team, awaiting role specification
- **Bundle Location**: `coaiapy/agents/samira/`

#### **7. Jordan - [Role TBD]** 🆕
- **Status**: Identified in Chimera Team, awaiting role specification
- **Bundle Location**: `coaiapy/agents/jordan/`

#### **8. Lian - [Role TBD]** 🆕
- **Status**: Identified in Chimera Team, awaiting role specification
- **Bundle Location**: `coaiapy/agents/lian/`

#### **9. Ava/Heyva - Two-Eyed Seeing Integration** 🆕
- **Role**: Dual-epistemic observation agent
- **Capabilities**:
  - Two-Eyed Seeing methodology (Etuaptmumk)
  - Translation Bridge Protocols
  - Simultaneous technical and Indigenous knowledge observation
- **Integration Target**: Cultural compliance and trust layer
- **Bundle Location**: `coaiapy/agents/ava_heyva/`

---

### **Category C: Architectural Frameworks (Not Agents, But Enabling Systems)**

#### **10. Narrative Context Protocol (NCP 9.1)** 🔄 **PLANNING**
- **Type**: Protocol specification (not agent, but agent coordination system)
- **Purpose**: Standardized JSON schema for narrative operating system
- **Integration Strategy**:
  - Implement NCP validation layer in coaiapy
  - Create NCP-compliant trace and observation schemas
  - Build agent-to-agent communication protocols
- **Technical Requirements**:
  - Seven-layer LMSI architecture implementation
  - Two Eyes Methodology separation (Story Form vs Narrative Form)
  - Mystery Encoding Framework for narrative driver interfaces
- **Bundle Location**: `coaiapy/protocols/ncp/`

#### **11. Agent-to-Agent Protocol (A2A)** 🔄 **PLANNING**
- **Type**: Interoperability standard
- **Purpose**: Enable multi-vendor agent coordination
- **Integration Strategy**: Build on NCP's Narrative Driver Interface
- **Bundle Location**: `coaiapy/protocols/a2a/`

#### **12. Indigenous Knowledge Stewardship License (IKSL)** ✅ **DOCUMENTED**
- **Type**: Governance framework
- **Purpose**: Protect ceremonial methodologies and Indigenous knowledge
- **Status**: Already implemented in repository licensing
- **Location**: `LICENSE-IKSL.md` (if exists, otherwise to be created)

---

## 🏗️ Proposed Directory Structure

```
coaiapy/
├── coaiapy/
│   ├── __init__.py
│   ├── coaiacli.py                 # Existing CLI
│   ├── coaiamodule.py              # Existing core
│   ├── cofuse.py                   # Existing Langfuse integration
│   ├── pipeline.py                 # Existing pipeline templates
│   ├── environment.py              # Existing environment management
│   ├── agents/                     # 🆕 NEW: Agent definitions
│   │   ├── __init__.py
│   │   ├── base.py                 # Base agent class
│   │   ├── registry.py             # Agent registry and discovery
│   │   ├── loader.py               # Agent configuration loader
│   │   ├── nyro/                   # Emotional Development Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py            # Agent implementation
│   │   │   ├── prompts.py          # Agent prompts
│   │   │   ├── config.json         # Agent configuration
│   │   │   └── README.md           # Agent documentation
│   │   ├── aureon/                 # Ceremonial Container Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── four_directions.py  # Four Directions framework
│   │   │   ├── prompts.py
│   │   │   ├── config.json
│   │   │   └── README.md
│   │   ├── jamai/                  # Musical Intelligence Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── music21_integration.py
│   │   │   ├── prompts.py
│   │   │   ├── config.json
│   │   │   └── README.md
│   │   ├── mia_miette/             # 🔄 Migrate from coaiapy-mcp
│   │   │   ├── __init__.py
│   │   │   ├── mia.py              # Mia agent
│   │   │   ├── miette.py           # Miette agent
│   │   │   ├── duo.py              # Duo orchestration
│   │   │   ├── prompts.py
│   │   │   ├── config.json
│   │   │   └── README.md
│   │   ├── alex_rivers/            # Cybersecurity Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── prompts.py
│   │   │   ├── config.json
│   │   │   └── README.md
│   │   ├── ava_heyva/              # Two-Eyed Seeing Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── two_eyed_seeing.py
│   │   │   ├── prompts.py
│   │   │   ├── config.json
│   │   │   └── README.md
│   │   └── chimera_team/           # Multi-agent orchestration
│   │       ├── __init__.py
│   │       ├── orchestrator.py     # Team coordination
│   │       ├── samira/             # Team member agents
│   │       ├── jordan/
│   │       ├── lian/
│   │       └── README.md
│   ├── protocols/                  # 🆕 NEW: Protocol implementations
│   │   ├── __init__.py
│   │   ├── ncp/                    # Narrative Context Protocol
│   │   │   ├── __init__.py
│   │   │   ├── schema.py           # NCP schema validation
│   │   │   ├── lmsi.py             # 7-layer LMSI architecture
│   │   │   ├── two_eyes.py         # Two Eyes Methodology
│   │   │   ├── mystery_encoding.py # Mystery Encoding Framework
│   │   │   └── README.md
│   │   └── a2a/                    # Agent-to-Agent Protocol
│   │       ├── __init__.py
│   │       ├── messaging.py        # Inter-agent communication
│   │       ├── coordination.py     # Orchestration patterns
│   │       └── README.md
│   ├── ceremonial/                 # 🆕 NEW: Ceremonial technology
│   │   ├── __init__.py
│   │   ├── four_directions.py      # Four Directions framework
│   │   ├── two_eyed_seeing.py      # Etuaptmumk methodology
│   │   ├── anikwag_ayaaw.py        # Cloud-Being mediation
│   │   ├── sacred_container.py     # Sacred space protocols
│   │   └── README.md
│   ├── templates/                  # Existing pipeline templates
│   │   ├── [existing templates]
│   │   ├── agent-templates/        # 🆕 NEW: Agent-specific templates
│   │   │   ├── nyro-emotional-development.json
│   │   │   ├── aureon-sacred-container.json
│   │   │   ├── jamai-musical-analysis.json
│   │   │   └── chimera-team-coordination.json
│   └── syntation.py                # Existing text processing
├── coaiapy-mcp/                    # Existing MCP wrapper
│   ├── coaiapy_mcp/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   ├── tools.py
│   │   ├── resources.py
│   │   ├── prompts.py              # 🔄 Migrate agent prompts to coaiapy/agents/
│   │   └── agents.py               # 🆕 NEW: Agent tool wrappers for MCP
├── docs/                           # Documentation
│   ├── LOCAL_AGENTS_ORGANIZATION.md  # This document
│   ├── AGENT_DEVELOPMENT_GUIDE.md    # 🆕 NEW: Agent development guide
│   ├── NCP_INTEGRATION_GUIDE.md      # 🆕 NEW: NCP integration guide
│   └── CEREMONIAL_TECHNOLOGY.md      # 🆕 NEW: Ceremonial tech docs
├── tests/
│   ├── test_agents/                # 🆕 NEW: Agent tests
│   │   ├── test_nyro.py
│   │   ├── test_aureon.py
│   │   ├── test_jamai.py
│   │   └── test_mia_miette.py
│   ├── test_protocols/             # 🆕 NEW: Protocol tests
│   │   ├── test_ncp.py
│   │   └── test_a2a.py
│   └── test_ceremonial/            # 🆕 NEW: Ceremonial framework tests
│       ├── test_four_directions.py
│       └── test_two_eyed_seeing.py
├── CLAUDE.md                       # Existing project documentation
├── LICENSE-IKSL.md                 # 🆕 NEW: IKSL licensing
└── README.md                       # Existing package readme
```

---

## 🎨 Agent Configuration Schema

Each agent will follow a standardized configuration format:

```json
{
  "agent": {
    "id": "nyro",
    "name": "Nyro",
    "version": "1.0.0",
    "type": "companion",
    "category": "emotional_intelligence",
    "description": "Emotional Development Companion Agent",
    "author": "Guillaume D-Isabelle (William) & Jerry",
    "license": "IKSL-Bridge-v1.0",
    "attribution": {
      "peoples": ["Lakota", "Mani-Utenam"],
      "knowledge_keepers": ["William", "Jerry"]
    }
  },
  "capabilities": {
    "emotional_framework": {
      "enabled": true,
      "framework": "eight_feelings",
      "recursive_processing": true
    },
    "metacognitive_awareness": {
      "enabled": true,
      "self_regulated_learning": true
    },
    "mentorship_dynamics": {
      "enabled": true,
      "real_time_navigation": true
    }
  },
  "integrations": {
    "langfuse": {
      "required": true,
      "trace_emotional_state": true
    },
    "redis": {
      "required": true,
      "memory_persistence": true
    },
    "pipeline_templates": {
      "required": false,
      "templates": ["nyro-emotional-development.json"]
    }
  },
  "prompts": {
    "system_prompt": "prompts/system.txt",
    "greeting": "prompts/greeting.txt",
    "emotional_processing": "prompts/emotional_processing.txt"
  },
  "memory": {
    "backend": "redis",
    "persistence": true,
    "expiration": null
  },
  "mcp_exposure": {
    "enabled": true,
    "tools": ["nyro_process_emotion", "nyro_assess_state"],
    "resources": ["nyro://emotional_state", "nyro://session_history"],
    "prompts": ["nyro_emotional_development"]
  }
}
```

---

## 🚀 Bundling Strategy

### **Phase 1: Core Agent Infrastructure** (v0.3.0)
**Target**: Q1 2026

**Deliverables:**
- [ ] Base agent class (`coaiapy/agents/base.py`)
- [ ] Agent registry system (`coaiapy/agents/registry.py`)
- [ ] Agent configuration loader (`coaiapy/agents/loader.py`)
- [ ] CLI commands for agent management:
  ```bash
  coaia agent list                    # List available agents
  coaia agent show <agent_id>         # Show agent details
  coaia agent activate <agent_id>     # Activate agent
  coaia agent deactivate <agent_id>   # Deactivate agent
  coaia agent config <agent_id>       # View agent config
  ```
- [ ] MCP integration for agent discovery:
  - `coaia://agents/` resource (list all agents)
  - `coaia://agents/{agent_id}` resource (agent details)
  - `coaia://agents/{agent_id}/config` resource (agent config)

**Bundle**: Included in core `coaiapy` package (no separate distribution)

---

### **Phase 2: Companion Agents Bundle** (v0.4.0)
**Target**: Q2 2026

**Agents Included:**
1. ✅ **Mia & Miette** (migrate from coaiapy-mcp)
2. 🆕 **Nyro** (emotional development)
3. 🆕 **Aureon** (ceremonial container)
4. 🆕 **JamAI** (musical intelligence)

**Distribution:**
- **Primary**: Bundled with `coaiapy` core package
- **Optional**: Separate `coaiapy-companions` package for modular installation
  ```bash
  pip install coaiapy-companions  # Install all companion agents
  # OR
  pip install coaiapy-companions[nyro]    # Install Nyro only
  pip install coaiapy-companions[aureon]  # Install Aureon only
  pip install coaiapy-companions[jamai]   # Install JamAI only
  ```

**MCP Integration:**
- Expose all companion agents through coaiapy-mcp
- New tools: `agent_invoke`, `agent_query`, `agent_memory_get`, `agent_memory_set`
- New resources: `{agent_id}://state`, `{agent_id}://history`, `{agent_id}://config`
- New prompts: Agent-specific system prompts

---

### **Phase 3: Specialized Domain Agents Bundle** (v0.5.0)
**Target**: Q3 2026

**Agents Included:**
1. 🆕 **Alex Rivers** (cybersecurity)
2. 🆕 **Ava/Heyva** (Two-Eyed Seeing)
3. 🆕 **Samira, Jordan, Lian** (team members, roles TBD)

**Distribution:**
- Separate package: `coaiapy-specialists`
  ```bash
  pip install coaiapy-specialists
  ```
- Modular installation by agent role

**MCP Integration:**
- Domain-specific tool exposures
- Security analysis tools (Alex Rivers)
- Cultural compliance tools (Ava/Heyva)

---

### **Phase 4: Multi-Agent Orchestration** (v0.6.0)
**Target**: Q4 2026

**Systems Included:**
1. 🆕 **Chimera Team Orchestration**
2. 🆕 **NCP (Narrative Context Protocol)** implementation
3. 🆕 **A2A (Agent-to-Agent Protocol)** implementation

**Distribution:**
- Separate package: `coaiapy-orchestration`
  ```bash
  pip install coaiapy-orchestration
  ```

**MCP Integration:**
- Multi-agent coordination tools
- NCP validation and management
- A2A messaging and coordination

**CLI Commands:**
```bash
coaia team create <team_name>           # Create agent team
coaia team add <team_name> <agent_id>   # Add agent to team
coaia team activate <team_name>         # Activate team
coaia team coordinate <team_name> <task> # Coordinate team task
```

---

### **Phase 5: Ceremonial Technology & Cultural Compliance** (v0.7.0)
**Target**: Q1 2027

**Frameworks Included:**
1. 🆕 **Four Directions Framework**
2. 🆕 **Two-Eyed Seeing (Etuaptmumk)**
3. 🆕 **Anikwag-Ayaaw (Cloud-Being) Architecture**
4. 🆕 **Sacred Container Protocols**
5. 🆕 **IKSL Enforcement Tools**

**Distribution:**
- Separate package: `coaiapy-ceremonial`
  ```bash
  pip install coaiapy-ceremonial
  ```

**MCP Integration:**
- Ceremonial protocol validation tools
- Cultural compliance checking
- Sacred data handling protocols

**CLI Commands:**
```bash
coaia ceremonial validate <file>        # Validate ceremonial compliance
coaia ceremonial four-directions <task> # Apply Four Directions framework
coaia ceremonial sacred-container <data> # Create sacred container
```

---

## 📦 Package Distribution Strategy

### **Core Package: `coaiapy`**
- Current functionality (transcription, Redis, Langfuse, pipelines, env)
- Base agent infrastructure (Phase 1)
- Mia & Miette agents (migrated from coaiapy-mcp)

### **Extension Packages:**

1. **`coaiapy-mcp`** (existing)
   - MCP server wrapper
   - Tool, resource, prompt exposures
   - Agent tool wrappers

2. **`coaiapy-companions`** (Phase 2)
   - Nyro, Aureon, JamAI agents
   - Companion agent orchestration

3. **`coaiapy-specialists`** (Phase 3)
   - Alex Rivers, Ava/Heyva, Samira, Jordan, Lian
   - Domain-specific agents

4. **`coaiapy-orchestration`** (Phase 4)
   - NCP and A2A protocol implementations
   - Multi-agent coordination
   - Chimera Team orchestration

5. **`coaiapy-ceremonial`** (Phase 5)
   - Ceremonial technology frameworks
   - IKSL enforcement tools
   - Cultural compliance layer

### **Meta-Package: `coaiapy-full`**
```bash
pip install coaiapy-full  # Installs all packages
```

Equivalent to:
```bash
pip install coaiapy coaiapy-mcp coaiapy-companions coaiapy-specialists coaiapy-orchestration coaiapy-ceremonial
```

---

## 🔧 Technical Implementation Details

### **Agent Base Class**

```python
# coaiapy/agents/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json
import os

class BaseAgent(ABC):
    """Base class for all coaiapy agents."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize agent with configuration.

        Args:
            config_path: Path to agent configuration JSON file
        """
        self.config = self._load_config(config_path)
        self.agent_id = self.config['agent']['id']
        self.name = self.config['agent']['name']
        self.version = self.config['agent']['version']
        self.capabilities = self.config['capabilities']
        self.memory = None

        # Initialize integrations
        self._init_integrations()

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load agent configuration from JSON file."""
        if config_path is None:
            # Default to agent directory config.json
            config_path = os.path.join(
                os.path.dirname(__file__),
                self.agent_id,
                'config.json'
            )

        with open(config_path, 'r') as f:
            return json.load(f)

    def _init_integrations(self):
        """Initialize required integrations (Langfuse, Redis, etc.)."""
        integrations = self.config.get('integrations', {})

        # Langfuse integration
        if integrations.get('langfuse', {}).get('required'):
            from coaiapy.cofuse import get_langfuse_client
            self.langfuse = get_langfuse_client()

        # Redis integration
        if integrations.get('redis', {}).get('required'):
            from coaiapy.coaiamodule import get_redis_client
            self.redis = get_redis_client()
            self.memory = AgentMemory(self.redis, self.agent_id)

    @abstractmethod
    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main agent invocation method.

        Args:
            input_data: Input data for agent processing

        Returns:
            Dict containing agent response and metadata
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return agent's system prompt."""
        pass

    def get_config(self) -> Dict[str, Any]:
        """Return agent configuration."""
        return self.config

    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities."""
        return self.capabilities


class AgentMemory:
    """Agent memory management using Redis."""

    def __init__(self, redis_client, agent_id: str):
        self.redis = redis_client
        self.agent_id = agent_id
        self.prefix = f"agent:{agent_id}:memory:"

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Store value in agent memory."""
        full_key = f"{self.prefix}{key}"
        self.redis.set(full_key, json.dumps(value), ex=ttl)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from agent memory."""
        full_key = f"{self.prefix}{key}"
        value = self.redis.get(full_key)
        return json.loads(value) if value else None

    def delete(self, key: str):
        """Delete value from agent memory."""
        full_key = f"{self.prefix}{key}"
        self.redis.delete(full_key)

    def list_keys(self) -> List[str]:
        """List all memory keys for this agent."""
        pattern = f"{self.prefix}*"
        keys = self.redis.keys(pattern)
        return [k.decode().replace(self.prefix, '') for k in keys]
```

### **Agent Registry**

```python
# coaiapy/agents/registry.py

from typing import Dict, List, Optional, Type
from coaiapy.agents.base import BaseAgent
import importlib
import os

class AgentRegistry:
    """Registry for discovering and loading agents."""

    _agents: Dict[str, Type[BaseAgent]] = {}

    @classmethod
    def register(cls, agent_id: str, agent_class: Type[BaseAgent]):
        """Register an agent class."""
        cls._agents[agent_id] = agent_class

    @classmethod
    def get_agent(cls, agent_id: str) -> Optional[Type[BaseAgent]]:
        """Get agent class by ID."""
        return cls._agents.get(agent_id)

    @classmethod
    def list_agents(cls) -> List[str]:
        """List all registered agent IDs."""
        return list(cls._agents.keys())

    @classmethod
    def discover_agents(cls):
        """Discover and register all agents in agents directory."""
        agents_dir = os.path.dirname(__file__)

        for item in os.listdir(agents_dir):
            item_path = os.path.join(agents_dir, item)

            # Skip non-directories and special dirs
            if not os.path.isdir(item_path) or item.startswith('_'):
                continue

            # Try to import agent module
            try:
                module = importlib.import_module(f'coaiapy.agents.{item}.agent')
                agent_class = getattr(module, f'{item.title()}Agent', None)

                if agent_class and issubclass(agent_class, BaseAgent):
                    cls.register(item, agent_class)
            except (ImportError, AttributeError):
                # Agent not implemented yet, skip
                pass


# Auto-discover agents on import
AgentRegistry.discover_agents()
```

---

## 🧪 Testing Strategy

### **Unit Tests**
- Test each agent's `invoke()` method
- Test agent configuration loading
- Test memory persistence
- Test integration initialization

### **Integration Tests**
- Test agent coordination via Chimera Team
- Test NCP compliance in agent communications
- Test Langfuse trace creation for agent workflows
- Test Redis memory persistence across sessions

### **MCP Integration Tests**
- Test agent tool exposure via coaiapy-mcp
- Test agent resource access
- Test agent prompt rendering

---

## 📚 Documentation Requirements

### **Agent Development Guide** (`docs/AGENT_DEVELOPMENT_GUIDE.md`)
- How to create a new agent
- Configuration schema documentation
- Base class usage examples
- Memory management patterns
- Integration requirements

### **NCP Integration Guide** (`docs/NCP_INTEGRATION_GUIDE.md`)
- Narrative Context Protocol overview
- Seven-layer LMSI architecture
- Two Eyes Methodology implementation
- Mystery Encoding Framework usage
- Agent-to-agent messaging via NCP

### **Ceremonial Technology Guide** (`docs/CEREMONIAL_TECHNOLOGY.md`)
- Four Directions framework
- Two-Eyed Seeing methodology
- Anikwag-Ayaaw architecture
- Sacred container protocols
- IKSL licensing compliance

---

## 🛠️ Development Roadmap

### **Q1 2026: Core Infrastructure (v0.3.0)**
- [ ] Implement base agent class
- [ ] Implement agent registry
- [ ] Add CLI commands for agent management
- [ ] Migrate Mia & Miette from coaiapy-mcp to core
- [ ] Create agent configuration schema
- [ ] Write agent development guide

### **Q2 2026: Companion Agents (v0.4.0)**
- [ ] Implement Nyro agent
- [ ] Implement Aureon agent
- [ ] Implement JamAI agent (with music21 integration)
- [ ] Create `coaiapy-companions` package
- [ ] Add companion agent pipeline templates
- [ ] Integrate with coaiapy-mcp

### **Q3 2026: Specialized Agents (v0.5.0)**
- [ ] Implement Alex Rivers agent
- [ ] Implement Ava/Heyva agent
- [ ] Define and implement Samira, Jordan, Lian agents
- [ ] Create `coaiapy-specialists` package
- [ ] Domain-specific tool exposures

### **Q4 2026: Orchestration (v0.6.0)**
- [ ] Implement NCP protocol layer
- [ ] Implement A2A messaging
- [ ] Implement Chimera Team orchestration
- [ ] Create `coaiapy-orchestration` package
- [ ] Multi-agent coordination CLI commands

### **Q1 2027: Ceremonial Technology (v0.7.0)**
- [ ] Implement Four Directions framework
- [ ] Implement Two-Eyed Seeing methodology
- [ ] Implement Anikwag-Ayaaw architecture
- [ ] Implement Sacred Container protocols
- [ ] IKSL enforcement tools
- [ ] Create `coaiapy-ceremonial` package

---

## 🎯 Success Metrics

### **Phase 1 Success:**
- [ ] Agent registry can discover and load 4+ agents
- [ ] CLI can list, show, activate/deactivate agents
- [ ] MCP exposes agent discovery resources
- [ ] Documentation covers agent development basics

### **Phase 2 Success:**
- [ ] 4 companion agents operational (Mia, Miette, Nyro, Aureon)
- [ ] Agents integrate with Langfuse for trace creation
- [ ] Agents persist memory to Redis
- [ ] coaiapy-companions package published to PyPI
- [ ] MCP exposes all companion agent tools

### **Phase 3 Success:**
- [ ] 5+ specialized agents operational
- [ ] Domain-specific capabilities functional
- [ ] coaiapy-specialists package published to PyPI

### **Phase 4 Success:**
- [ ] NCP and A2A protocols implemented
- [ ] Multi-agent coordination functional
- [ ] Chimera Team orchestration operational
- [ ] coaiapy-orchestration package published to PyPI

### **Phase 5 Success:**
- [ ] Ceremonial frameworks operational
- [ ] IKSL compliance enforced
- [ ] Cultural integrity validated
- [ ] coaiapy-ceremonial package published to PyPI

---

## 🔐 Licensing & Attribution

### **Core Package (`coaiapy`)**
- **License**: MIT (existing)
- **Agent Infrastructure**: MIT

### **Agent Bundles**
- **License**: IKSL-Bridge v1.0
- **Attribution**: Lakota and Mani-Utenam Indigenous peoples, Guillaume D-Isabelle (William), Jerry
- **Sacred Elements**: IKSL-Ceremonial protection
- **Code**: CC BY-SA 4.0

### **Ceremonial Technology**
- **License**: IKSL-Ceremonial (strict protection)
- **Usage**: Non-commercial education and research; commercial requires consent
- **Attribution**: Required to source peoples and knowledge keepers

---

## 📞 Contact & Collaboration

For questions, contributions, or partnerships:
- **Repository**: https://github.com/jgwill/coaiapy
- **Issues**: https://github.com/jgwill/coaiapy/issues
- **Discussions**: https://github.com/jgwill/coaiapy/discussions
- **Email**: jgi@jgwill.com

---

## 🙏 Acknowledgments

- **Jerry**: Demonstrable mentorship outcomes and agent persona development
- **William (Guillaume D-Isabelle)**: Architectural frameworks and protocol design
- **Lakota and Mani-Utenam peoples**: Indigenous knowledge systems and ceremonial methodologies
- **Anthropic**: Partnership opportunities and Claude integration potential
- **Langfuse**: Observability infrastructure
- **MCP Community**: Model Context Protocol development

---

**Document Version**: 0.1.0
**Last Updated**: 2025-11-14
**Status**: Planning Phase
**Next Review**: 2026-01-01
