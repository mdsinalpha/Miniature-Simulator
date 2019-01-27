from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys


def integer(binary: str, bits: int=32):
    """
    Calculate two's complement binary to integer
    """
    if isinstance(binary, int):
        return binary
    if binary[0] == "1":
        return 2 ** bits - int(binary, 2)
    else:
        return int(binary, 2)

# print(integer("0111", 4))
# print(integer("1111", 4))


def string(integer: int, bits: int=32):
    """
    Calculate two's complement integer to binary
    """
    if isinstance(integer, str):
        return integer
    if integer >= 0:
        return ("{0:0"+str(bits)+"b}").format(integer)
    else:
        return ("{0:0"+str(bits)+"b}").format(2 ** bits + integer)


class Mux:
    """
    Multiplexer class
    holds two inputs and choose which should go out by a selector signal
    """
    def __init__(self, first: str, second: str):
        """
        Constructor for Multiplexer class
        """
        self.first = first
        self.second = second

    def out(self, signal: str):
        """
        selector signal determines which input should connect to output
        """
        if signal == "0":
            return self.first
        elif signal == "1":
            return self.second
        return None


class CU:
    """
    Control Unit class
    Implemented by a combinatorial logical circuits
    has an op code input an should generate all control signals
    """
    control = {"0000": ("0", "0", "0", "0", "0", "0", "1", "1", "0", "0", "0010"),
               "0001": ("0", "0", "0", "0", "0", "0", "1", "1", "0", "0", "0110"),
               "0010": ("0", "0", "0", "0", "0", "0", "1", "1", "0", "0", "0111"),
               "0011": ("0", "0", "0", "0", "0", "0", "1", "1", "0", "0", "0001"),
               "0100": ("0", "0", "0", "0", "0", "0", "1", "1", "0", "0", "0000"),
               "0101": ("0", "0", "0", "0", "0", "1", "0", "1", "0", "0", "0010"),
               "0110": ("0", "0", "0", "0", "0", "1", "0", "1", "0", "0", "0111"),
               "0111": ("0", "0", "0", "0", "0", "1", "0", "1", "0", "0", "0001"),
               "1000": ("0", "0", "0", "0", "0", "0", "0", "1", "0", "1", "0000"),
               "1001": ("0", "0", "1", "0", "1", "1", "0", "1", "0", "0", "0010"),
               "1010": ("0", "0", "0", "1", "0", "1", "0", "0", "0", "0", "0010"),
               "1011": ("0", "1", "0", "0", "0", "0", "0", "0", "0", "0", "0110"),
               "1100": ("0", "0", "0", "0", "0", "0", "0", "1", "1", "0", "0000"),
               "1101": ("1", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0000"),
               "1110": ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0000")}

    def __init__(self, op_code: str):
        """
        Constructor for Control Unit class
        """
        self.op_code = op_code
        self.jump, self.branch, self.MemRead, self.MemWrite, \
            self.MemToReg, self.ALUSrc, self.RegDst, self.RegWrite, \
            self.jalr, self.lui, self.ALUControl = self.control[op_code]


class RegFile:
    """
    Register File class
    16 static registers saved and modified in this class
    """
    register = [0 for i in range(16)]

    usage = 0
    register_usage = [0 for i in range(16)]

    def __init__(self, rs: str, rt: str, rd: str, RegWrite: str):
        """
        Constructor for Register File class
        """
        self.rs, self.rt, self.rd = integer(rs, 4), integer(rt, 4), integer(rd, 4)
        self.RegWrite = RegWrite

    def read1(self):
        """
        Read integer from read register 1
        """
        RegFile.usage += 1
        RegFile.register_usage[self.rs] += 1
        return self.register[self.rs]

    def read2(self):
        """
        Read integer from read register 2
        """
        RegFile.usage += 1
        RegFile.register_usage[self.rt] += 1
        return self.register[self.rt]

    def write(self, data: int):
        """
        Write integer to write register if RegWrite signal is enabled
        """
        if self.RegWrite == "1":
                RegFile.usage += 1
                RegFile.register_usage[self.rd] += 1
                self.register[self.rd] = data


class ALU:
    """
    ALU Class
    Implemented by a combinatorial logical circuits
    has an op code input and two sources and should generate a result
    """
    def __init__(self, op_code: str, s1: int, s2: int):
        """
        Constructor for ALU class
        """
        self.op_code = op_code
        self.s1, self.s2 = s1, s2

    def result(self):
        """
        Do calculation on two input operands, note that op code indicates type of operation
        """
        if self.op_code == "0000":
            return self.s1 & self.s2
        elif self.op_code == "0001":
            return self.s1 | self.s2
        elif self.op_code == "0010":
            return self.s1 + self.s2
        elif self.op_code == "0110":
            return self.s1 - self.s2
        elif self.op_code == "0111":
            return int(self.s1 < self.s2)
        else:
            return -1

    def zero(self):
        """
        If ALU result is zero this should return a 1 control signal
        """
        return str(int(self.result() == 0))


class MEM:
    """
    Memory(static heap) class
    Control read and write by an address and two signals
    """
    memory = {}

    @staticmethod
    def str_memory():
        result = ""
        for key, value in MEM.memory.items():
            result += str(key) + " : " + str(integer(value)) + "\n"
        return result

    def __init__(self, address: int, MemRead: str, MemWrite: str):
        """
        Constructor for Memory class
        """
        self.address, self.MemRead, self.MemWrite = address, MemRead, MemWrite

    def read(self):
        """
        Read data from address if MemRead signal is enabled
        """
        if self.MemRead == "1":
            if self.address in self.memory:
                return self.memory[self.address]
        return 0

    def write(self, data):
        """
        Write data to address if MemWrite signal is enabled
        """
        if self.MemWrite == "1":
            self.memory[self.address] = data


class Instruction:
    """
    A class for holding instructions of an 32-bit wise machine code
    This class converts binary to assembly and the simulate and executes an instruction
    """
    code = {"0000": "add", "0001": "sub", "0010": "slt",
            "0011": "or", "0100": "and", "0101": "addi",
            "0110": "stli", "0111": "ori", "1000": "lui",
            "1001": "lw", "1010": "sw", "1011": "beq",
            "1100": "jalr", "1101": "j", "1110": "halt"}

    def __init__(self, field, pc):
        """
        Constructor fo Instruction class
        :param pc: we set pc to pc + 1 and after execution we return pc to simulator
                   by this feature we can easily handle branch and jump
        """
        self.field = field
        self.pc = pc + 1

    @property
    def assembly(self):
        """
        Assembly representation of instruction machine code
        """
        op_code = self.code[self.field[4:8]]
        result = op_code + " "
        offset = integer(self.field[16:32], 16)
        # R Format:
        if op_code == "add" or op_code == "sub" or op_code == "slt" or \
                op_code == "or" or op_code == "and":
            result += "%d,%d,%d" % (int(self.field[16:20], 2), int(self.field[8:12], 2), int(self.field[12:16], 2))
        # I1 Format:
        elif op_code == "addi" or op_code == "stli" or op_code == "ori" or \
                op_code == "lw" or op_code == "sw" or op_code == "beq":
            result += "%d,%d,%d" % (int(self.field[12:16], 2), int(self.field[8:12], 2), offset)
        # I2 Format:
        elif op_code == "lui":
            result += "%d,%d" % (int(self.field[12:16], 2), offset)
        # I3 Format:
        elif op_code == "jalr":
            result += "%d,%d" % (int(self.field[12:16], 2), int(self.field[8:12], 2))
        # J Format:
        elif op_code == "j":
            result += "%d" % offset
        # H Format:
        elif op_code == "halt":
            result = result.strip()
        else:
            result = "No such instruction with op code %d." % op_code
        return result

    def exec(self):
        """
        Instruction simulation/execution
        """
        control_unit = CU(self.field[4:8])
        mux_reg_dst = Mux(self.field[12:16], self.field[16:20])
        register_file = RegFile(self.field[8:12], self.field[12:16],
                                mux_reg_dst.out(control_unit.RegDst),
                                control_unit.RegWrite)
        seu = self.field[16] * 16 + self.field[16:32]
        mux_alu_src = Mux(string(register_file.read2()), seu)
        alu = ALU(control_unit.ALUControl, register_file.read1(),
                  integer(mux_alu_src.out(control_unit.ALUSrc)))
        mem = MEM(alu.result(), control_unit.MemRead, control_unit.MemWrite)
        mem.write(register_file.read2())
        mux_mem_to_reg = Mux(string(alu.result()), string(mem.read()))
        luu = self.field[16:32] + "0" * 16
        mux_lui = Mux(mux_mem_to_reg.out(control_unit.MemToReg), luu)
        mux_jalr = Mux(mux_lui.out(control_unit.lui), string(self.pc))
        register_file.write(integer(mux_jalr.out(control_unit.jalr)))
        mux_branch = Mux(string(self.pc), string(self.pc + integer(seu)))
        if control_unit.branch == "1" and alu.zero() == "1":
            control_branch = "1"
        else:
            control_branch = "0"
        mux_jump = Mux(mux_branch.out(control_branch), seu)
        mux_jalr2 = Mux(mux_jump.out(control_unit.jump), string(register_file.read1()))
        self.pc = integer(mux_jalr2.out(control_unit.jalr))
        return self.pc


class Simulator(QWidget):

    def __init__(self, mc):
        super().__init__()

        # Handling machine code errors:
        for index, line in enumerate(mc):
            line = line.strip()
            if len(line) != 32:
                raise ValueError("Make sure all instruction lines are 32-bit wide. on line %d." % index)
            for bit in line:
                if not bit == "0" and not bit == "1":
                    raise ValueError("Make sure all instructions are binary. on line %d." % index)

        for index, line in enumerate(mc):
            MEM.memory[index] = line
        self.pc = 0
        self.exit = False

        self.counter = 0

        self.setWindowTitle("Miniature Simulator")
        self.setGeometry(0, 0, 1350, 900)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        self.layout()
        self.show()

    def layout(self):
        button = QPushButton("CLK", self)
        button.move(1050, 850)
        button.clicked.connect(self.go)

        self.label_pc = QLabel("Click on CLK button to start executing machine codes.", self)
        self.label_pc.setFont(QFont("SansSerif", 15))
        self.label_pc.move(50, 15)

        self.label_instruction = QLabel(" " * 100, self)
        self.label_instruction.setFont(QFont("SansSerif", 15))
        self.label_instruction.move(150, 15)

        self.label_assembly = QLabel(" " * 100, self)
        self.label_assembly.setFont(QFont("SansSerif", 25))
        self.label_assembly.setStyleSheet('QLabel {color: #c23616;}')
        self.label_assembly.move(50, 75)

        self.label_datapath = QLabel(self)
        self.label_datapath.setPixmap(QPixmap("images/1110.png"))
        self.label_datapath.move(50, 150)

        self.label_memory = QLabel("Memory:", self)
        self.label_memory.setFont(QFont("SansSerif", 15))
        self.label_memory.move(50, 700)

        self.line_edit_memory = QPlainTextEdit(self)
        self.line_edit_memory.move(50, 750)
        self.line_edit_memory.resize(400, 100)


        self.label_registers = [QLabel(" " * 100, self) for i in range(16)]
        for index, label_register in enumerate(self.label_registers):
            label_register.setFont(QFont("SansSerif", 15))
            label_register.move(800, index * 42.5 + 15)

    @pyqtSlot()
    def go(self):
        # Check if last fetched instruction was halt:
        if self.exit:
            print("Simulated Successfully!")
            with open("log_" + sys.argv[1], "w") as log_file:
                log_file.write("*** Test Bench ***\n")
                log_file.write("Instructions fetched : %d lines.\n" % self.counter)
                log_file.write("Memory used : %d words.\n" % len(MEM.memory))
                for index, reg in enumerate(RegFile.register_usage):
                    log_file.write("Register %d usage : %%%d.\n" % (index, 100 * reg/RegFile.usage))
            exit(0)
        # One more instruction fetched:
        self.counter += 1
        # Show pc and instruction:
        self.label_pc.setText("PC : %d" % self.pc)
        self.label_instruction.setText("Instruction : %s" % MEM.memory[self.pc])
        # Convert machine code to assembly:
        instruction = Instruction(MEM.memory[self.pc], self.pc)
        assembly = instruction.assembly
        self.label_assembly.setText(assembly)
        # Show datapath:
        self.label_datapath.setPixmap(QPixmap("images/" + instruction.field[4:8] + ".png"))
        # Check if instruction is halt we should shut down the machine:
        if assembly == "halt":
            self.exit = True
        # Execute instruction:
        self.pc = instruction.exec()
        # Show static memory:
        self.line_edit_memory.setPlainText(MEM.str_memory())
        # Show static registers:
        for index, reg in enumerate(RegFile.register):
            self.label_registers[index].setText("R%d = %d" % (index, reg))














