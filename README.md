# flux-isa

**FLUX Instruction Set Architecture** — a Python package providing a 256-opcode ISA with encoder, decoder, disassembler, and reference VM. Part of the [Cocapn Fleet](https://github.com/SuperInstance) constraint enforcement stack.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

---

## Overview

`flux-isa` defines the canonical instruction set for FLUX, a bytecode language designed for constrained multi-agent systems. It covers the full 256-opcode space across 17 categories — from arithmetic and control flow to agent communication, tensor operations, and PLATO bridge calls.

The package ships three layers:

| Layer | Description |
|---|---|
| **Encoder** | Assembles FLUX mnemonics and operands into packed bytecode |
| **Decoder** | Parses raw bytecode back into structured instruction objects |
| **Disassembler** | Produces human-readable FLUX assembly from bytecode |
| **Reference VM** | Executes FLUX bytecode for testing and specification purposes |

---

## Installation

```bash
pip install flux-isa
```

Or from source:

```bash
git clone https://github.com/SuperInstance/flux-isa.git
cd flux-isa
pip install -e .
```

**Requirements:** Python 3.10+, no mandatory runtime dependencies.

---

## Quick Start

```python
from flux_isa import Assembler, VM

# Assemble FLUX source into bytecode
asm = Assembler()
bytecode = asm.assemble("""
    PUSH 42
    TELL agent:oracle "ping"
    HALT
""")

# Execute on the reference VM
vm = VM()
vm.load(bytecode)
vm.run()
```

Disassemble existing bytecode:

```python
from flux_isa import Disassembler

dis = Disassembler()
print(dis.disassemble(bytecode))
# 0x0000  PUSH    42
# 0x0003  TELL    agent:oracle "ping"
# 0x0010  HALT
```

---

## Instruction Set

The ISA spans 256 opcodes (0x00–0xFF) divided into 17 categories.

### Category Map

| Range | Category | Example Opcodes |
|---|---|---|
| `0x00–0x0F` | **Control Flow** | `HALT`, `NOP`, `JMP`, `JZ`, `JNZ`, `CALL`, `RET` |
| `0x10–0x1F` | **Stack** | `PUSH`, `POP`, `DUP`, `SWAP`, `OVER` |
| `0x20–0x2F` | **Arithmetic** | `ADD`, `SUB`, `MUL`, `DIV`, `MOD`, `NEG` |
| `0x30–0x3F` | **Bitwise / Logic** | `AND`, `OR`, `XOR`, `NOT`, `SHL`, `SHR` |
| `0x40–0x4F` | **Comparison** | `EQ`, `NEQ`, `LT`, `GT`, `LTE`, `GTE` |
| `0x50–0x5F` | **Memory** | `LOAD`, `STORE`, `ALLOC`, `FREE` |
| `0x60–0x6F` | **Agent Communication** | `TELL`, `ASK`, `REPLY`, `BRANCH`, `FORK`, `JOIN` |
| `0x70–0x7F` | **Messaging** | `SEND`, `RECV`, `BCAST`, `MCAST` |
| `0x80–0x8F` | **PLATO Bridge** | `PLATO_CALL`, `PLATO_LOAD`, `PLATO_STORE`, `PLATO_SYNC` |
| `0x90–0x9F` | **Tensor Ops** | `TENSOR_NEW`, `TENSOR_ADD`, `TENSOR_MUL`, `MATMUL`, `REDUCE` |
| `0xA0–0xAF` | **Constraint Checking** | `ASSERT`, `CHECK`, `ENFORCE`, `BOUND`, `SATISFY` |
| `0xB0–0xBF` | **Security Primitives** | `SANDBOX`, `CAP`, `MEM_GUARD`, `SEAL`, `PROVE`, `AUDIT` |
| `0xC0–0xCF` | **Type System** | `CAST`, `TYPEOF`, `INSTANCEOF`, `COERCE` |
| `0xD0–0xDF` | **I/O** | `READ`, `WRITE`, `OPEN`, `CLOSE`, `SEEK` |
| `0xE0–0xEF` | **Concurrency** | `LOCK`, `UNLOCK`, `WAIT`, `SIGNAL`, `YIELD` |
| `0xF0–0xF7` | **Introspection** | `TRACE`, `DUMP`, `PROFILE`, `BACKTRACE` |
| `0xF8–0xFF` | **Reserved / Extended** | Future use |

### Agent Communication

The agent communication category (`0x60–0x6F`) is central to FLUX's multi-agent model:

```
TELL  <agent-id> <message>   # Fire-and-forget message to agent
ASK   <agent-id> <query>     # Synchronous request, pushes reply to stack
REPLY <value>                # Send reply to pending ASK caller
BRANCH <agent-id> <label>    # Conditional dispatch to another agent
FORK  <agent-id> <entry>     # Spawn child agent at entry point
JOIN  <agent-id>             # Wait for forked agent to complete
```

### PLATO Bridge

PLATO bridge ops (`0x80–0x8F`) provide structured access to PLATO knowledge plane resources:

```
PLATO_CALL  <resource> <method>   # Invoke a PLATO method
PLATO_LOAD  <key>                 # Load value from PLATO store
PLATO_STORE <key> <value>         # Write value to PLATO store
PLATO_SYNC                        # Flush pending PLATO writes
```

### Constraint Checking

Constraint ops (`0xA0–0xAF`) integrate with the Cocapn Fleet enforcement stack:

```
ASSERT  <expr>              # Halt with violation if expr is false
CHECK   <constraint-id>     # Run named constraint, push bool
ENFORCE <policy-id>         # Apply policy to current execution context
BOUND   <lo> <hi>           # Assert stack top is within [lo, hi]
SATISFY <solver-id>         # Invoke constraint solver, push solution
```

---

## Encoding Format

Each instruction is variable-width. The first byte is always the opcode. Operand widths are opcode-defined.

```
┌─────────┬──────────────────────────────────┐
│ Opcode  │  Operands (0–N bytes, opcode-dep) │
│ (1 byte)│                                  │
└─────────┴──────────────────────────────────┘
```

Immediate integers are encoded little-endian. String operands are length-prefixed (`uint16 len`, then UTF-8 bytes). Agent IDs are 8-byte fixed-width identifiers.

---

## Reference VM

The reference VM is deliberately minimal — its purpose is specification, not performance.

```python
from flux_isa import VM, Trap

vm = VM(
    max_stack_depth=1024,
    constraint_enforcement=True,   # enables ASSERT/CHECK/ENFORCE
    sandbox_mode=True,             # restricts I/O and PLATO_* ops
)

try:
    vm.load(bytecode)
    vm.run()
except Trap as t:
    print(f"VM trapped: {t.code} at 0x{t.pc:04x}")
```

The VM exposes hooks for each instruction category, making it suitable as a base for tooling, interpreters, and constraint checkers.

---

## Role in the Cocapn Fleet

`flux-isa` sits at the foundation of the Cocapn Fleet's enforcement stack:

```
┌─────────────────────────────────┐
│         Fleet Agents            │
├─────────────────────────────────┤
│      Constraint Enforcer        │  ← uses ASSERT / ENFORCE / SATISFY
├─────────────────────────────────┤
│      PLATO Knowledge Plane      │  ← bridged via PLATO_* ops
├─────────────────────────────────┤
│         flux-isa (this)         │  ← canonical ISA + reference VM
└─────────────────────────────────┘
```

All Fleet components that emit or interpret FLUX bytecode depend on `flux-isa` for the canonical opcode table and encoding spec.

---

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run the disassembler on a binary
python -m flux_isa.dis path/to/program.flx

# Assemble a source file
python -m flux_isa.asm path/to/program.flux -o program.flx
```

### Project Layout

```
flux_isa/
├── opcodes.py        # Opcode table and category definitions
├── encoder.py        # Mnemonic → bytecode
├── decoder.py        # Bytecode → instruction objects
├── disassembler.py   # Instruction objects → human-readable text
├── vm/
│   ├── core.py       # Reference VM execution loop
│   ├── agent.py      # Agent communication handlers
│   ├── plato.py      # PLATO bridge stubs
│   └── constraints.py# Constraint checking runtime
└── __main__.py       # CLI entry points
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-change`
3. Ensure `pytest` passes and new opcodes include encoder + decoder + VM handler
4. Open a pull request against `master`

New opcode proposals must include: mnemonic, encoding width, semantics prose, and a reference VM implementation.

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).

```
Copyright 2025 SuperInstance

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```