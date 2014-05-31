"""
The MIT License (MIT)

Copyright (c) 2014 Mohab Usama

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import itertools

from exceptions import InvalidInstruction


INST_TERM = ';'  # instruction terminator character
ARG_SEP = ','  # instruction arg separator character
ELEM_SEP = '.'  # instruction arg element separator character (e.g. 4.size)

# @TODO: enumerate instruction set


def decode_arg(encoded_arg):
    """
    Decode an Instruction arg.

    example:
    >> arg = decode_arg('4.size')
    >> arg == 'size'
    >> True

    :return: str
    """
    if -1 == encoded_arg.find(ELEM_SEP):
        raise InvalidInstruction('Instruction element separator not found.')

    length, arg = encoded_arg.split(ELEM_SEP)
    if len(arg) != int(length):
        raise InvalidInstruction(
            'Instruction arg (%s) has invalid length.' % encoded_arg)

    return arg


def encode_arg(arg):
    """
    Encode argument to be sent in a valid Guacamole instruction.

    example:
    >> arg = encode_arg('size')
    >> arg == '4.size'
    >> True

    :return: str
    """
    return ELEM_SEP.join([str(len(str(arg))), str(arg)])


class GuacamoleInstruction(object):

    def __init__(self, opcode, *args, **kwargs):
        self.opcode = opcode
        self.args = args

    @classmethod
    def load(cls, instruction):
        """
        Loads a new Instruction from encoded instruction.

        :return: Instruction()
        """
        if not instruction.endswith(INST_TERM):
            raise InvalidInstruction('Instruction termination not found.')

        elems = instruction[:-1].split(ARG_SEP)

        args = [decode_arg(arg) for arg in elems]

        return cls(args[0], *args[1:])

    def encode(self):
        """
        Prepare the instruction to be sent over the wire.

        :return: str
        """
        instruction_iter = itertools.chain([self.opcode], self.args)

        elems = ARG_SEP.join(encode_arg(arg) for arg in instruction_iter)

        return elems + INST_TERM

    def __str__(self):
        return self.encode()
