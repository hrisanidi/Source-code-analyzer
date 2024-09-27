"""
Brno University of Technology
Project: IPP1
Author: Vladislav Khrisanov (xkhris00)
"""

import sys
import re
from abc import ABC, abstractmethod


# an abstract class defining the implementation part in the bridge pattern
class OperandPart(ABC):
    def __init__(self, contents):
        self.contents = contents

    @abstractmethod
    def is_valid(self) -> bool:
        pass


class Frame(OperandPart):
    def is_valid(self):
        if self.contents == 'GF' or self.contents == 'TF' or self.contents == 'LF':
            return True


class Name(OperandPart):
    def is_valid(self):
        if re.search("^[a-zA-Z_\\-$&%*!?][a-zA-Z0-9_\\-$&%*!?]*$", self.contents):
            return True


class TypeNoNil(OperandPart):
    def is_valid(self):
        if self.contents == 'bool' or self.contents == 'int' or self.contents == 'string':
            return True


class TypeAndValue(OperandPart):
    def __init__(self, type_value, value):
        super().__init__(value)
        self.__type = type_value
        self.__value = value

    def is_valid(self):
        match self.__type:
            case 'bool':
                if self.contents == 'true' or self.contents == 'false':
                    return True
            case 'int':
                # inspired by official PHP regex expressions for the integer:
                # https://www.php.net/manual/en/language.types.integer.php
                if re.search("^[+-]?(0|[1-9][0-9]*(_[0-9]+)*|0[oO]?[0-7]+(_[0-7]+)*|0[xX][0-9a-fA-F]+(_[0-9a-fA-F]+)*)$", self.contents):
                    return True
            case 'nil':
                if self.contents == 'nil':
                    return True
            case 'string':
                if self.contents != "":
                    # enclosed in quotation marks
                    if self.contents[0] == "\"" or self.contents[0] == "\'" \
                            or self.contents[-1] == "\"" or self.contents[-1] == "\'":
                        return False

                    # invalid escape sequence
                    if re.findall("(\\\\+[0-9]{0,2})(?!\\d)", self.contents):
                        return False

                return True
            case _:
                return False


# an abstract class defining the abstraction part in the bridge pattern
class Operand(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def process(self, contents):
        pass

    @staticmethod
    def error():
        sys.exit(23)


class Var(Operand):
    def __init__(self):
        self.xml_arg_type = 'var'
        self.xml_arg_value = None

    def process(self, contents):
        # check if the '@' separator is present
        parts = contents.split('@', 1)
        if len(parts) != 2:
            self.error()

        # check the frame and the name
        if Frame(parts[0]).is_valid() and Name(parts[1]).is_valid():
            self.xml_arg_value = contents
        else:
            self.error()


class Symb(Operand):
    def __init__(self):
        self.xml_arg_type = None
        self.xml_arg_value = None

    def process(self, contents):
        # check if the '@' separator is present
        parts = contents.split('@', 1)
        if len(parts) != 2:
            self.error()

        # provided symbol is a variable
        if Frame(parts[0]).is_valid() and Name(parts[1]).is_valid():
            self.xml_arg_type = 'var'
            self.xml_arg_value = contents
        # provided symbol is a constant
        elif TypeAndValue(parts[0], parts[1]).is_valid():
            self.xml_arg_type = parts[0]
            self.xml_arg_value = parts[1]
        else:
            self.error()


class Label(Operand):
    def __init__(self):
        self.xml_arg_type = 'label'
        self.xml_arg_value = None

    def process(self, contents):
        # check the label name
        if Name(contents).is_valid():
            self.xml_arg_value = contents
        else:
            self.error()


class Type(Operand):
    def __init__(self):
        self.xml_arg_type = 'type'
        self.xml_arg_value = None

    def process(self, contents):
        # check the type
        if TypeNoNil(contents).is_valid():
            self.xml_arg_value = contents
        else:
            self.error()
