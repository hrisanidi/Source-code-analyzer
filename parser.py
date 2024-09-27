"""
Brno University of Technology
Project: IPP1
Author: Vladislav Khrisanov (xkhris00)
"""

import sys
import xml.etree.ElementTree as et
from stats import StatsCollector
from operand import *


# contains the main logic of the script
class Parser:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Parser, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.__header = False
        self.__opcode = None
        self.__operands = None
        self.__order = 0
        self.__comment_cnt = 0
        self.__xml_root = None
        self.__stats = None

    # analyze the provided file line by line
    def run(self):
        # no input file
        if sys.stdin.isatty() is True:
            sys.exit(21)

        for line in sys.stdin:
            # deal with blank lines and comments
            line = line.strip().split("#", 1)
            if len(line) == 2:
                self.__comment_cnt += 1
            if line[0] == '':
                continue
            line = line[0]

            # header detection
            if self.__header is False:
                if line.strip().upper() == ".IPPCODE24":
                    self.__header = True
                    self.__xml_start()
                    continue
                else:
                    sys.exit(21)

            line = line.split()
            self.__opcode = line[0].upper()

            # invalid opcode format
            if not self.__opcode.isalnum():
                sys.exit(23)

            # process the instruction
            self.__order += 1
            self.__process_operands(line[1:])
            self.__xml_add_instruction()

        # the file was scanned
        if self.__header:
            self.__xml_output()
            # process statistics if needed
            if self.__stats is not None:
                self.__stats.set_loc_comments(self.__order, self.__comment_cnt)
                self.__stats.write_results()
        else:
            sys.exit(21)

    def __process_operands(self, received_operands):
        # get the expected operand sequence for the provided opcode
        operand_sequence = self.__match_opcode()

        # instruction with no operands
        if operand_sequence is None:
            if len(received_operands) == 0:
                self.__operands = operand_sequence
                # gather statistics if needed
                if self.__stats is not None:
                    self.__stats.process_instruction(self.__opcode, None, self.__order)
                return
            else:
                sys.exit(23)

        # instructions with at least 1 operand
        if len(operand_sequence) == len(received_operands):
            for i in range(len(operand_sequence)):
                operand_sequence[i].process(received_operands[i])
            self.__operands = operand_sequence
            # gather statistics if needed
            if self.__stats is not None:
                self.__stats.process_instruction(self.__opcode, self.__operands[0].xml_arg_value, self.__order)
        else:
            sys.exit(23)

    def __match_opcode(self):
        match self.__opcode:
            case 'MOVE' | 'INT2CHAR' | 'STRLEN' | 'TYPE' | 'NOT':
                return tuple((Var(), Symb()))
            case 'CREATEFRAME' | 'PUSHFRAME' | 'POPFRAME' | 'RETURN' | 'BREAK':
                return None
            case 'DEFVAR' | 'POPS':
                return tuple((Var(),))
            case 'CALL' | 'LABEL' | 'JUMP':
                return tuple((Label(),))
            case 'JUMPIFEQ' | 'JUMPIFNEQ':
                return tuple((Label(), Symb(), Symb()))
            case 'PUSHS' | 'WRITE' | 'EXIT' | 'DPRINT':
                return tuple((Symb(),))
            case 'ADD' | 'SUB' | 'MUL' | 'IDIV' | 'LT' | 'GT' | 'EQ' | 'AND' | 'OR' | \
                 'STRI2INT' | 'CONCAT' | 'GETCHAR' | 'SETCHAR':
                return tuple((Var(), Symb(), Symb()))
            case 'READ':
                return tuple((Var(), Type()))
            case _:
                sys.exit(22)

    def __xml_start(self):
        self.__xml_root = et.Element("program")
        self.__xml_root.set("language", "IPPcode24")

    def __xml_add_instruction(self):
        instruction = et.SubElement(self.__xml_root, "instruction", order=str(self.__order), opcode=self.__opcode)

        if self.__operands is not None:
            for i in range(len(self.__operands)):
                tag = "arg" + str(i + 1)
                argument = et.SubElement(instruction, tag, type=self.__operands[i].xml_arg_type)
                argument.text = self.__operands[i].xml_arg_value
        else:
            return

    def __xml_output(self):
        et.indent(self.__xml_root)
        tree = et.tostring(self.__xml_root, encoding="UTF-8", xml_declaration=True).decode()
        sys.stdout.write(tree)

    def gather_stats(self):
        self.__stats = StatsCollector()
        self.__stats.initialize()
