# Agent Bundling Roadmap - Executive Summary

**Reference**: [Full Documentation](./LOCAL_AGENTS_ORGANIZATION.md)
**Status**: Planning Phase
**Version**: 0.1.0
**Date**: 2025-11-14

---

## 🎯 Vision

Transform coaiapy into a comprehensive local agent ecosystem with 12+ specialized AI agents, multi-agent orchestration, and Indigenous-informed ceremonial technology frameworks.

---

## 📦 Bundling Strategy

### **Core Packages**

1. **`coaiapy`** (core)
   - Existing functionality + base agent infrastructure
   - Mia & Miette companion agents

2. **`coaiapy-mcp`** (existing)
   - MCP server wrapper exposing all capabilities

3. **`coaiapy-companions`** (v0.4.0 - Q2 2026)
   - Nyro (emotional intelligence)
   - Aureon (ceremonial container)
   - JamAI (musical intelligence)

4. **`coaiapy-specialists`** (v0.5.0 - Q3 2026)
   - Alex Rivers (cybersecurity)
   - Ava/Heyva (Two-Eyed Seeing)
   - Samira, Jordan, Lian (team members)

5. **`coaiapy-orchestration`** (v0.6.0 - Q4 2026)
   - NCP (Narrative Context Protocol)
   - A2A (Agent-to-Agent Protocol)
   - Chimera Team coordination

6. **`coaiapy-ceremonial`** (v0.7.0 - Q1 2027)
   - Four Directions framework
   - Two-Eyed Seeing methodology
   - Sacred Container protocols
   - IKSL enforcement tools

7. **`coaiapy-full`** (meta-package)
   - Installs all packages above

---

## 🗓️ Timeline

| Phase | Version | Target | Deliverables |
|-------|---------|--------|--------------|
| Phase 1: Core Infrastructure | v0.3.0 | Q1 2026 | Base agent class, registry, CLI commands |
| Phase 2: Companion Agents | v0.4.0 | Q2 2026 | Nyro, Aureon, JamAI agents |
| Phase 3: Specialized Agents | v0.5.0 | Q3 2026 | Alex Rivers, Ava/Heyva, team members |
| Phase 4: Orchestration | v0.6.0 | Q4 2026 | NCP, A2A, Chimera Team |
| Phase 5: Ceremonial Tech | v0.7.0 | Q1 2027 | Four Directions, IKSL enforcement |

---

## 🧩 Agent Inventory

### **Companion Agents** (Emotional & Cognitive Support)
1. ✅ **Mia & Miette** - Dual AI embodiment (currently in coaiapy-mcp)
2. 🆕 **Nyro** - Emotional development companion
3. 🆕 **Aureon** - Spiritual grounding and ceremonial container
4. 🆕 **JamAI** - Musical intelligence with music21 integration

### **Specialized Agents** (Domain Expertise)
5. 🆕 **Alex Rivers** - Cybersecurity researcher (Isolation Protector)
6. 🆕 **Ava/Heyva** - Two-Eyed Seeing integration agent
7. 🆕 **Samira** - Team member (role TBD)
8. 🆕 **Jordan** - Team member (role TBD)
9. 🆕 **Lian** - Team member (role TBD)

### **Orchestration Systems** (Not agents, but coordination frameworks)
10. 🔄 **NCP** - Narrative Context Protocol (7-layer LMSI architecture)
11. 🔄 **A2A** - Agent-to-Agent Protocol (interoperability standard)
12. 🔄 **Chimera Team** - Multi-agent coordination system

---

## 🏗️ Proposed Directory Structure (Condensed)

```
coaiapy/
├── coaiapy/
│   ├── agents/                     # 🆕 NEW: Agent definitions
│   │   ├── base.py                 # Base agent class
│   │   ├── registry.py             # Agent discovery
│   │   ├── nyro/                   # Emotional Development Agent
│   │   ├── aureon/                 # Ceremonial Container Agent
│   │   ├── jamai/                  # Musical Intelligence Agent
│   │   ├── mia_miette/             # Dual AI Embodiment (migrated)
│   │   ├── alex_rivers/            # Cybersecurity Agent
│   │   ├── ava_heyva/              # Two-Eyed Seeing Agent
│   │   └── chimera_team/           # Multi-agent orchestration
│   ├── protocols/                  # 🆕 NEW: Protocol implementations
│   │   ├── ncp/                    # Narrative Context Protocol
│   │   └── a2a/                    # Agent-to-Agent Protocol
│   ├── ceremonial/                 # 🆕 NEW: Ceremonial technology
│   │   ├── four_directions.py
│   │   ├── two_eyed_seeing.py
│   │   ├── anikwag_ayaaw.py
│   │   └── sacred_container.py
│   └── templates/agent-templates/  # 🆕 NEW: Agent-specific templates
├── coaiapy-mcp/
│   └── coaiapy_mcp/
│       └── agents.py               # 🆕 NEW: Agent tool wrappers for MCP
├── docs/
│   ├── LOCAL_AGENTS_ORGANIZATION.md  # Complete documentation
│   ├── AGENT_BUNDLING_ROADMAP.md     # This document
│   ├── AGENT_DEVELOPMENT_GUIDE.md    # 🆕 NEW: How to create agents
│   ├── NCP_INTEGRATION_GUIDE.md      # 🆕 NEW: NCP protocol guide
│   └── CEREMONIAL_TECHNOLOGY.md      # 🆕 NEW: Ceremonial frameworks
└── tests/
    ├── test_agents/                # 🆕 NEW: Agent tests
    ├── test_protocols/             # 🆕 NEW: Protocol tests
    └── test_ceremonial/            # 🆕 NEW: Ceremonial framework tests
```

---

## 🚀 CLI Commands Preview

### **Phase 1: Agent Management**
```bash
coaia agent list                    # List available agents
coaia agent show <agent_id>         # Show agent details
coaia agent activate <agent_id>     # Activate agent
coaia agent deactivate <agent_id>   # Deactivate agent
coaia agent config <agent_id>       # View agent configuration
```

### **Phase 2-3: Agent Invocation**
```bash
coaia agent invoke nyro --input "Feeling overwhelmed"
coaia agent invoke aureon --ceremony "four-directions"
coaia agent invoke jamai --analyze "song.mid"
coaia agent invoke alex_rivers --scan "network_logs.txt"
```

### **Phase 4: Team Orchestration**
```bash
coaia team create <team_name>           # Create agent team
coaia team add <team_name> <agent_id>   # Add agent to team
coaia team activate <team_name>         # Activate team
coaia team coordinate <team_name> <task> # Coordinate team task
```

### **Phase 5: Ceremonial Technology**
```bash
coaia ceremonial validate <file>        # Validate ceremonial compliance
coaia ceremonial four-directions <task> # Apply Four Directions framework
coaia ceremonial sacred-container <data> # Create sacred container
```

---

## 🔧 Installation Preview

### **Core Installation**
```bash
pip install coaiapy  # Includes base agent infrastructure + Mia & Miette
```

### **Modular Installation**
```bash
pip install coaiapy-companions        # All companion agents
pip install coaiapy-companions[nyro]  # Nyro only
pip install coaiapy-specialists       # All specialized agents
pip install coaiapy-orchestration     # NCP, A2A, Chimera Team
pip install coaiapy-ceremonial        # Ceremonial frameworks
```

### **Full Installation**
```bash
pip install coaiapy-full  # Everything
```

---

## 📊 Success Metrics

### **Phase 1 (Q1 2026)**
- [ ] Agent registry discovers 4+ agents
- [ ] CLI agent management commands operational
- [ ] MCP agent discovery resources exposed

### **Phase 2 (Q2 2026)**
- [ ] 4 companion agents operational
- [ ] Langfuse trace integration working
- [ ] Redis memory persistence functional
- [ ] coaiapy-companions published to PyPI

### **Phase 3 (Q3 2026)**
- [ ] 5+ specialized agents operational
- [ ] Domain-specific tools functional
- [ ] coaiapy-specialists published to PyPI

### **Phase 4 (Q4 2026)**
- [ ] NCP and A2A protocols implemented
- [ ] Multi-agent coordination functional
- [ ] coaiapy-orchestration published to PyPI

### **Phase 5 (Q1 2027)**
- [ ] Ceremonial frameworks operational
- [ ] IKSL compliance enforced
- [ ] coaiapy-ceremonial published to PyPI

---

## 🔐 Licensing

- **Core Package**: MIT (existing)
- **Agent Bundles**: IKSL-Bridge v1.0
- **Ceremonial Technology**: IKSL-Ceremonial (strict protection)
- **Attribution**: Lakota and Mani-Utenam Indigenous peoples, Guillaume D-Isabelle (William), Jerry

---

## 📚 Documentation

- **Complete Plan**: [LOCAL_AGENTS_ORGANIZATION.md](./LOCAL_AGENTS_ORGANIZATION.md)
- **Agent Development**: Coming in Phase 1
- **NCP Integration**: Coming in Phase 4
- **Ceremonial Technology**: Coming in Phase 5

---

## 🎯 Next Actions (Immediate)

1. **Review** this roadmap with project stakeholders
2. **Prioritize** agents for Phase 2 implementation
3. **Define** roles for Samira, Jordan, Lian agents
4. **Document** existing Mia & Miette prompt specifications
5. **Plan** music21 integration architecture for JamAI
6. **Begin** Phase 1 implementation (Q1 2026)

---

## 📞 Contact

- **Repository**: https://github.com/jgwill/coaiapy
- **Issues**: https://github.com/jgwill/coaiapy/issues
- **Email**: jgi@jgwill.com

---

**Last Updated**: 2025-11-14
**Status**: Planning Complete, Ready for Phase 1 Implementation
**Next Milestone**: v0.3.0 (Core Infrastructure) - Q1 2026
