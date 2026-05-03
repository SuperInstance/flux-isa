#!/usr/bin/env python3
"""
flux-isa — FLUX ISA v2.0 Encoder/Decoder/VM Reference
Fixed 4-byte instruction set for the FLUX fleet-native computing ecosystem.

Usage:
    from flux_isa import ISADecoder, ISAEncoder, FluxVM
    
    # Encode
    bytecode = ISAEncoder.encode(0x08, 0, 1, 2)  # IADD R0, R1, R2
    
    # Decode
    opcode, a, b, c = ISADecoder.decode(bytecode)
    
    # Execute
    vm = FluxVM()
    vm.load(bytecode)
    vm.run()
"""

import json, struct, time
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

@dataclass
class Instruction:
    opcode: int
    operand_a: int
    operand_b: int
    operand_c: int
    mnemonic: str = ""
    category: str = ""

class ISADecoder:
    """Decode FLUX bytecode to instructions."""
    
    def __init__(self, isa_path: str = None):
        self.isa = self._load_isa(isa_path)
    
    def _load_isa(self, path: str = None) -> Dict:
        if path:
            with open(path) as f:
                return json.load(f)
        # Fallback: load from embedded minimal spec
        return {"instruction_format": {"size_bytes": 4}}
    
    def decode(self, bytecode: bytes) -> Instruction:
        """Decode a single 4-byte instruction."""
        if len(bytecode) != 4:
            raise ValueError(f"Invalid instruction size: {len(bytecode)} (expected 4)")
        
        opcode, a, b, c = struct.unpack("BBBB", bytecode)
        
        # Look up mnemonic from ISA spec
        hex_key = f"0x{opcode:02X}"
        spec = self.isa.get("opcodes", {}).get(hex_key, {})
        
        return Instruction(
            opcode=opcode,
            operand_a=a,
            operand_b=b,
            operand_c=c,
            mnemonic=spec.get("mnemonic", f"UNK_{opcode:02X}"),
            category=spec.get("category", "unknown")
        )
    
    def decode_sequence(self, bytecode: bytes) -> List[Instruction]:
        """Decode a sequence of instructions."""
        instructions = []
        for i in range(0, len(bytecode), 4):
            if i + 4 <= len(bytecode):
                instructions.append(self.decode(bytecode[i:i+4]))
        return instructions
    
    def disassemble(self, bytecode: bytes) -> List[str]:
        """Disassemble bytecode to human-readable assembly."""
        lines = []
        for i, instr in enumerate(self.decode_sequence(bytecode)):
            hex_str = f"{instr.opcode:02X} {instr.operand_a:02X} {instr.operand_b:02X} {instr.operand_c:02X}"
            
            # Format operands based on mnemonic
            ops = self._format_operands(instr)
            lines.append(f"{i*4:04X}:  {hex_str}    {instr.mnemonic:12s} {ops}")
        return lines
    
    def _format_operands(self, instr: Instruction) -> str:
        spec = self.isa.get("opcodes", {}).get(f"0x{instr.opcode:02X}", {})
        ops = spec.get("operands", [])
        
        if not ops:
            return ""
        
        parts = []
        for i, op_name in enumerate(ops):
            val = [instr.operand_a, instr.operand_b, instr.operand_c][i]
            
            if "imm16" in op_name:
                # Combine B and C for 16-bit immediate
                imm = (instr.operand_c << 8) | instr.operand_b
                parts.append(f"#{imm}")
            elif "off16" in op_name:
                off = struct.unpack("h", struct.pack("BB", instr.operand_b, instr.operand_c))[0]
                parts.append(f"{off:+d}")
            elif "addr16" in op_name:
                addr = (instr.operand_c << 8) | instr.operand_b
                parts.append(f"0x{addr:04X}")
            elif "Rd" in op_name or "Rs" in op_name:
                parts.append(f"R{val}")
            elif "Fd" in op_name or "Fa" in op_name or "Fb" in op_name:
                parts.append(f"F{val}")
            elif "agent_id" in op_name:
                parts.append(f"A{val}")
            elif "room_id" in op_name:
                parts.append(f"room{val}")
            elif "model_id" in op_name:
                parts.append(f"model{val}")
            elif "kernel_id" in op_name:
                parts.append(f"K{val}")
            elif "number" in op_name:
                parts.append(f"#{val}")
            elif "cycles" in op_name:
                parts.append(f"#{val}")
            elif "error_code" in op_name:
                parts.append(f"E{val}")
            elif "trace_id" in op_name:
                parts.append(f"T{val}")
            elif "lock_id" in op_name:
                parts.append(f"L{val}")
            elif "event_mask" in op_name:
                parts.append(f"0x{val:02X}")
            elif "port_reg" in op_name:
                parts.append(f"port{val}")
            elif "bc_start" in op_name:
                parts.append(f"0x{val:02X}")
            elif "agent_type" in op_name:
                parts.append(f"type{val}")
            elif "config_reg" in op_name:
                parts.append(f"R{val}")
            elif "payload_reg" in op_name:
                parts.append(f"R{val}")
            elif "timeout_reg" in op_name:
                parts.append(f"R{val}")
            elif "grid_reg" in op_name:
                parts.append(f"R{val}")
            elif "input_reg" in op_name:
                parts.append(f"R{val}")
            elif "query_reg" in op_name:
                parts.append(f"R{val}")
            elif "float_imm" in op_name:
                parts.append(f"#{val}")
            elif "tile_id" in op_name:
                parts.append(f"tile{val}")
            elif "offset8" in op_name:
                parts.append(f"+{val}")
            elif "addr8" in op_name:
                parts.append(f"[{val}]")
            else:
                parts.append(f"{val}")
        
        return ", ".join(parts)

class ISAEncoder:
    """Encode FLUX instructions to bytecode."""
    
    @staticmethod
    def encode(opcode: int, a: int = 0, b: int = 0, c: int = 0) -> bytes:
        """Encode a single 4-byte instruction."""
        return struct.pack("BBBB", opcode & 0xFF, a & 0xFF, b & 0xFF, c & 0xFF)
    
    @staticmethod
    def movi(rd: int, imm16: int) -> bytes:
        """Encode MOVI Rd, imm16."""
        return ISAEncoder.encode(0x02, rd, imm16 & 0xFF, (imm16 >> 8) & 0xFF)
    
    @staticmethod
    def iadd(rd: int, ra: int, rb: int) -> bytes:
        """Encode IADD Rd, Ra, Rb."""
        return ISAEncoder.encode(0x08, rd, ra, rb)
    
    @staticmethod
    def isub(rd: int, ra: int, rb: int) -> bytes:
        return ISAEncoder.encode(0x09, rd, ra, rb)
    
    @staticmethod
    def jmp(offset: int) -> bytes:
        """Encode JMP offset (16-bit signed)."""
        lo = offset & 0xFF
        hi = (offset >> 8) & 0xFF
        return ISAEncoder.encode(0x3A, 0, lo, hi)
    
    @staticmethod
    def halt() -> bytes:
        return ISAEncoder.encode(0x70)
    
    @staticmethod
    def tell(agent_id: int, payload_reg: int) -> bytes:
        return ISAEncoder.encode(0x50, agent_id, payload_reg)
    
    @staticmethod
    def plato_write(room_id: int, rs: int) -> bytes:
        return ISAEncoder.encode(0xB1, room_id, rs)

class FluxVM:
    """Reference VM for FLUX ISA v2.0."""
    
    def __init__(self):
        self.registers = [0] * 16  # R0-R15
        self.float_regs = [0.0] * 16  # F0-F15
        self.memory = bytearray(65536)  # 64KB addressable memory
        self.pc = 0
        self.sp = 0xFF00  # Stack grows downward from top
        self.fp = 0xFF00
        self.flags = {"z": False, "n": False, "c": False, "v": False}
        self.running = False
        self.bytecode = b""
        self.decoder = ISADecoder()
        self.tiles_submitted = 0
        self.messages_sent = 0
    
    def load(self, bytecode: bytes):
        """Load bytecode into VM."""
        self.bytecode = bytecode
        self.pc = 0
    
    def step(self) -> bool:
        """Execute one instruction. Returns True if halted."""
        if self.pc >= len(self.bytecode):
            return True
        
        instr = self.decoder.decode(self.bytecode[self.pc:self.pc+4])
        self.pc += 4
        
        return self._execute(instr)
    
    def _execute(self, instr: Instruction) -> bool:
        """Execute a single instruction. Returns True if halted."""
        op = instr.opcode
        a, b, c = instr.operand_a, instr.operand_b, instr.operand_c
        
        if op == 0x00:  # NOP
            pass
        
        elif op == 0x01:  # MOV Rd, Rs
            self.registers[a] = self.registers[b]
        
        elif op == 0x02:  # MOVI Rd, imm16
            imm = (c << 8) | b
            self.registers[a] = imm
        
        elif op == 0x08:  # IADD Rd, Ra, Rb
            result = self.registers[b] + self.registers[c]
            self.registers[a] = result & 0xFFFFFFFF
            self._set_flags(result)
        
        elif op == 0x09:  # ISUB Rd, Ra, Rb
            result = self.registers[b] - self.registers[c]
            self.registers[a] = result & 0xFFFFFFFF
            self._set_flags(result)
        
        elif op == 0x0A:  # IMUL
            result = self.registers[b] * self.registers[c]
            self.registers[a] = result & 0xFFFFFFFF
            self._set_flags(result)
        
        elif op == 0x0B:  # IDIV
            if self.registers[c] != 0:
                self.registers[a] = self.registers[b] // self.registers[c]
            else:
                self.registers[a] = 0
        
        elif op == 0x0E:  # INC
            self.registers[a] = (self.registers[a] + 1) & 0xFFFFFFFF
        
        elif op == 0x0F:  # DEC
            self.registers[a] = (self.registers[a] - 1) & 0xFFFFFFFF
        
        elif op == 0x20:  # AND
            result = self.registers[b] & self.registers[c]
            self.registers[a] = result
            self._set_flags(result)
        
        elif op == 0x21:  # OR
            result = self.registers[b] | self.registers[c]
            self.registers[a] = result
            self._set_flags(result)
        
        elif op == 0x22:  # XOR
            result = self.registers[b] ^ self.registers[c]
            self.registers[a] = result
            self._set_flags(result)
        
        elif op == 0x24:  # SHL
            self.registers[a] = (self.registers[b] << (self.registers[c] & 0x1F)) & 0xFFFFFFFF
        
        elif op == 0x25:  # SHR
            self.registers[a] = (self.registers[b] >> (self.registers[c] & 0x1F)) & 0xFFFFFFFF
        
        elif op == 0x2D:  # CMP
            result = self.registers[a] - self.registers[b]
            self._set_flags(result)
        
        elif op == 0x30:  # JZ
            if self.registers[a] == 0:
                offset = struct.unpack("h", struct.pack("BB", b, c))[0]
                self.pc = (self.pc + offset) & 0xFFFF
        
        elif op == 0x31:  # JNZ
            if self.registers[a] != 0:
                offset = struct.unpack("h", struct.pack("BB", b, c))[0]
                self.pc = (self.pc + offset) & 0xFFFF
        
        elif op == 0x3A:  # JMP
            offset = struct.unpack("h", struct.pack("BB", b, c))[0]
            self.pc = (self.pc + offset) & 0xFFFF
        
        elif op == 0x3B:  # CALL
            addr = (c << 8) | b
            self.registers[15] = self.pc  # Link register
            self.pc = addr
        
        elif op == 0x3C:  # RET
            self.pc = self.registers[15]
        
        elif op == 0x40:  # LOAD Rd, [Ra+offset8]
            addr = (self.registers[b] + c) & 0xFFFF
            self.registers[a] = struct.unpack("I", self.memory[addr:addr+4])[0]
        
        elif op == 0x41:  # STORE Rs, [Ra+offset8]
            addr = (self.registers[b] + c) & 0xFFFF
            self.memory[addr:addr+4] = struct.pack("I", self.registers[a])
        
        elif op == 0x50:  # TELL
            self.messages_sent += 1
        
        elif op == 0x53:  # BROADCAST
            self.messages_sent += 1
        
        elif op == 0x70:  # HALT
            return True
        
        elif op == 0x71:  # YIELD
            pass  # Cooperative multitasking hook
        
        elif op == 0x72:  # SLEEP
            pass  # Would sleep for `a` cycles
        
        elif op == 0x80:  # SYSCALL
            self._syscall(a)
        
        elif op == 0xB1:  # PLATO_WRITE
            self.tiles_submitted += 1
        
        return False
    
    def _set_flags(self, result: int):
        self.flags["z"] = (result & 0xFFFFFFFF) == 0
        self.flags["n"] = (result & 0x80000000) != 0
    
    def _syscall(self, number: int):
        if number == 1:  # print
            print(f"[VM] R0={self.registers[0]}")
        elif number == 2:  # get_time
            self.registers[8] = int(time.time())
    
    def run(self, max_steps: int = 10000):
        """Run until HALT or max steps."""
        self.running = True
        steps = 0
        while self.running and steps < max_steps:
            if self.step():
                break
            steps += 1
        self.running = False
        return steps
    
    def get_state(self) -> Dict:
        return {
            "pc": self.pc,
            "registers": self.registers[:8],
            "flags": self.flags,
            "tiles_submitted": self.tiles_submitted,
            "messages_sent": self.messages_sent
        }

def demo():
    print("=== FLUX ISA v2.0 Demo ===\n")
    
    # Build a simple program: factorial(5)
    encoder = ISAEncoder()
    bytecode = b""
    bytecode += encoder.movi(0, 5)      # R0 = 5 (n)
    bytecode += encoder.movi(1, 1)      # R1 = 1 (result)
    bytecode += encoder.iadd(1, 1, 0)   # R1 = R1 * R0 (using ADD for demo)
    bytecode += encoder.encode(0x0F, 0) # DEC R0
    bytecode += encoder.jmp(-8)         # JMP back (would need proper loop)
    bytecode += encoder.halt()          # HALT
    
    print("Bytecodes:")
    for i in range(0, len(bytecode), 4):
        chunk = bytecode[i:i+4]
        print(f"  {i:04X}: {' '.join(f'{b:02X}' for b in chunk)}")
    
    print("\nDisassembly:")
    decoder = ISADecoder()
    for line in decoder.disassemble(bytecode):
        print(f"  {line}")
    
    print("\nExecution:")
    vm = FluxVM()
    vm.load(bytecode)
    steps = vm.run(max_steps=10)
    print(f"  Steps executed: {steps}")
    print(f"  Final state: {vm.get_state()}")

if __name__ == "__main__":
    demo()
