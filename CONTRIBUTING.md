# Contributing to FLUX ISA

> *256 opcodes. 17 categories. One canonical instruction set for constrained multi-agent systems.*

## Quick Start

FLUX ISA is a Python package providing the canonical opcode table, encoder, decoder, disassembler, and reference VM for the FLUX bytecode language.

### Prerequisites
- Python 3.10+
- `pip` with `hatchling` support

### Install for Development

```bash
# Clone
git clone https://github.com/SuperInstance/flux-isa.git
cd flux-isa

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify
pytest
python -m flux_isa.dis examples/sample.flx  # if example exists
```

## Making Changes

1. **Fork the repo**
2. **Create a feature branch** (`git checkout -b feat/my-change` — note: `feat/` prefix per convention)
3. **Make your changes**
4. **Test** — `pytest` (all tests must pass)
5. **Commit** (`git commit -m "feat: add my feature"`)
6. **Push** (`git push origin feat/my-change`)
7. **Open a PR against `master`**

## Code Style

### Python
- Python 3.10+ with type hints
- Format with `ruff format` (line length 88)
- Lint with `ruff check`
- Docstrings for all public classes and functions

### Opcode Development Process

New opcodes are the most common type of contribution. Each opcode proposal must include:

1. **Mnemonic** — Short, descriptive name (e.g., `MATMUL`, `ENFORCE`, `BCAST`)
2. **Opcodes** — Must fit in the 256-opcode space (0x00–0xFF)
3. **Category** — Maps to one of the 17 categories (see README)
4. **Encoding width** — How many bytes the instruction takes (opcode + operands)
5. **Semantics prose** — Plain English description of what the instruction does
6. **Reference VM handler** — Implementation in `flux_isa/vm/`:
   - `vm/core.py` for new execution loop handlers
   - `vm/agent.py` for agent communication ops
   - `vm/plato.py` for PLATO bridge ops
   - `vm/constraints.py` for constraint checking ops
7. **Encoder/Decoder update** — Add to `encoder.py` and `decoder.py`
8. **Tests** — Each opcode needs encoder, decoder, and VM test cases

### Opcode Category Ranges

| Range | Category | File |
|-------|----------|------|
| 0x00–0x0F | Control Flow | `vm/core.py` |
| 0x10–0x1F | Stack | `vm/core.py` |
| 0x20–0x2F | Arithmetic | `vm/core.py` |
| 0x30–0x3F | Bitwise / Logic | `vm/core.py` |
| 0x40–0x4F | Comparison | `vm/core.py` |
| 0x50–0x5F | Memory | `vm/core.py` |
| 0x60–0x6F | Agent Communication | `vm/agent.py` |
| 0x70–0x7F | Messaging | `vm/agent.py` |
| 0x80–0x8F | PLATO Bridge | `vm/plato.py` |
| 0x90–0x9F | Tensor Ops | `vm/core.py` |
| 0xA0–0xAF | Constraint Checking | `vm/constraints.py` |
| 0xB0–0xBF | Security Primitives | `vm/core.py` |
| 0xC0–0xCF | Type System | `vm/core.py` |
| 0xD0–0xDF | I/O | `vm/core.py` |
| 0xE0–0xEF | Concurrency | `vm/core.py` |
| 0xF0–0xF7 | Introspection | `vm/core.py` |
| 0xF8–0xFF | Reserved / Extended | `vm/core.py` |

## Testing

```bash
# Run full test suite
pytest

# With coverage
pytest --cov=flux_isa

# Run specific test
pytest tests/test_encoder.py -v

# Test opcode encoding round-trip
python -c "from flux_isa import Assembler, Disassembler; a=Assembler(); d=Disassembler(); print(d.disassemble(a.assemble('PUSH 42\\nHALT')))"
```

### Test Coverage Requirements
- Every opcode needs: encoder test + decoder test + VM execution test
- Round-trip tests (encode → decode → disassemble)
- Edge cases: invalid opcodes, overflow operands, empty bytecode
- Agent communication: test multi-agent scenarios

## Project Layout

```
flux_isa/
├── opcodes.py          # Opcode table and category definitions
├── encoder.py          # Mnemonic → bytecode
├── decoder.py          # Bytecode → instruction objects
├── disassembler.py     # Instruction objects → human-readable text
├── vm/
│   ├── core.py         # Reference VM execution loop
│   ├── agent.py        # Agent communication handlers
│   ├── plato.py        # PLATO bridge stubs
│   └── constraints.py  # Constraint checking runtime
├── __main__.py         # CLI entry points
└── tests/              # Test suite
```

## Role in the Cocapn Fleet

flux-isa sits at the foundation of the enforcement stack:

```
Fleet Agents → Constraint Enforcer → PLATO → flux-isa (canonical ISA)
```

All Fleet components that emit or interpret FLUX bytecode depend on this package for the canonical opcode table and encoding spec. Changes to opcodes must be coordinated with downstream consumers.

## Reporting Issues

Open an [Issue](https://github.com/SuperInstance/flux-isa/issues) with:
- Python version and OS
- Relevant opcode or test case
- Expected vs actual behavior

## Questions?

- Read the [README](README.md) for the full ISA reference
- Open a [Discussion](https://github.com/SuperInstance/flux-isa/discussions)
- Check existing [Issues](https://github.com/SuperInstance/flux-isa/issues)
