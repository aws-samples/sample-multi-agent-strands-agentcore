# Re:Invent Multi-Agent Tutorial

This directory contains **only the essential files** needed to run the four Re:Invent multi-agent notebooks.

## Directory Structure

```
reinvented/
├── requirements.txt                           # All dependencies
├── lab-01-multi-agent-system.ipynb          # Lab 1: Multi-Agent Foundation
├── lab-02-multi-agent-memory.ipynb          # Lab 2: Memory Integration  
├── lab-03-multi-agent-gateway.ipynb         # Lab 3: Gateway Integration
├── lab-04-multi-agent-runtime.ipynb         # Lab 4: Production Runtime
├── lab_helpers/                              # Supporting code
│   ├── shared/utils.py                       # Progress tracking (Lab 2)
│   ├── compatibility.py                     # Multi-agent compatibility (Lab 3)
│   ├── utils.py                             # Deployment utilities (Lab 4)
│   ├── lab2_multi_agent_memory.py          # Memory integration (Lab 4)
│   └── runtime/                             # Runtime deployment files (Lab 4)
│       ├── orchestrator_runtime.py
│       ├── customer_support_runtime.py
│       └── knowledge_base_runtime.py
├── scripts/                                  # Infrastructure scripts (Lab 3+)
│   ├── prereq.sh                           # REQUIRED for Lab 3
│   └── utils.py
└── prerequisite/                            # Infrastructure templates (Lab 3+)
    ├── infrastructure.yaml
    ├── cognito.yaml
    └── lambda/
```

## How to Run Each Lab

### Lab 1: Multi-Agent System Foundation
**Completely self-contained** - no setup required!

```bash
cd reinvented
pip install -r requirements.txt
jupyter notebook lab-01-multi-agent-system.ipynb
```

### Lab 2: Multi-Agent Memory Integration
Builds on Lab 1, adds memory capabilities.

```bash
# Same as Lab 1 - memory hooks are included
jupyter notebook lab-02-multi-agent-memory.ipynb
```

### Lab 3: Multi-Agent Gateway Integration
**CRITICAL**: Must run infrastructure setup first!

```bash
# 1. Deploy infrastructure (REQUIRED)
./scripts/prereq.sh

# 2. Run the notebook
jupyter notebook lab-03-multi-agent-gateway.ipynb
```

### Lab 4: Production Multi-Agent Runtime
Requires all previous labs + Docker (optional).

```bash
# Builds on Lab 3 infrastructure
jupyter notebook lab-04-multi-agent-runtime.ipynb
```

## What Was Removed

This clean directory removes **hundreds of unnecessary files** including:
- ❌ Duplicate helper files
- ❌ Test files and debugging scripts  
- ❌ Documentation images (referenced but not essential)
- ❌ Progress tracking files
- ❌ Build artifacts and temporary files
- ❌ Alternative implementations
- ❌ Unused compatibility layers

## What Was Kept

Only the **absolute essentials**:
- ✅ The 4 main notebooks
- ✅ Single requirements.txt with all dependencies
- ✅ Minimal supporting code for each lab
- ✅ Infrastructure setup for Labs 3-4
- ✅ Runtime deployment files for Lab 4

## File Count Comparison

- **Original directory**: ~200+ files
- **Clean directory**: ~25 files
- **Reduction**: ~87% fewer files

## Prerequisites

- AWS account with appropriate permissions
- Python 3.10+ (3.12+ for Lab 4)
- AWS CLI configured
- Amazon Nova Pro enabled in Bedrock
- Docker/Finch/Podman (optional for Lab 4)

## Quick Start

1. **Start with Lab 1** (completely standalone)
2. **Progress to Lab 2** (adds memory)
3. **Run `./scripts/prereq.sh` before Lab 3** (sets up infrastructure)
4. **Continue to Lab 4** (production deployment)

Each lab builds on the previous one, but Lab 1 can run completely independently to understand the multi-agent concepts.

---

**This clean directory contains everything you need and nothing you don't!** 🎯
