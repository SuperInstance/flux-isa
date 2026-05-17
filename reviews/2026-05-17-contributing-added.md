# CONTRIBUTING.md Added — FLUX ISA

**Date:** 2026-05-17
**Action:** Created `CONTRIBUTING.md`

## Why This Repo Needed It

FLUX ISA defines the canonical 256-opcode instruction set for the entire Cocapn Fleet enforcement stack. It has a thorough README with a "Contributing" section, but that section was embedded in the README and limited to a brief 5-step workflow. It did not cover:

- Opcode development process (encoding width, semantics, VM handler)
- Category-to-file mapping (which VM file each opcode range goes in)
- Test coverage requirements per opcode
- Code style and linting rules
- Project layout explanation for contributors

For the foundational package that every FLUX bytecode consumer depends on, the contribution process needed to be formalized as a stand-alone document.

## What the Contribution Workflow Looks Like

1. Fork and create a feature branch (`feat/` prefix per convention)
2. Install with `pip install -e ".[dev]"`
3. Make changes — most commonly adding new opcodes
4. Each new opcode needs: mnemonic, encoding width, semantics prose, encoder/decoder update, VM handler, and tests
5. Run `pytest` and `ruff check`
6. Open PR against `master`

## Special Notes

- **256 Opcode Space**: The ISA is a fixed 256-opcode space divided into 17 categories. New opcodes must fit within their category's range (e.g., 0x60–0x6F for agent communication).
- **Foundation Package**: All Fleet components that emit or interpret FLUX bytecode depend on this package. Opcode changes must be coordinated with downstream consumers.
- **Reference VM**: The VM is deliberately minimal — it's a spec tool, not a production runtime. Focus on correctness and clarity, not performance.
- **Branch Convention**: Uses `feat/` prefix (not `feature/`), matching existing conventions in the repo.
