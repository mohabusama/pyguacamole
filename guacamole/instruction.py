"""
The MIT License (MIT)

Copyright (c)   2014 rescale
                2014 Mohab Usama

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


def decode_args(instruction):
    """
    Decode a whole Instruction args.

    example:
    >> args = decode_args('4.size,4.1024;')
    >> args == ['size', '1024']
    >> True

    :return: list
    """
    if not instruction.endswith(INST_TERM):
        raise InvalidInstruction('Instruction termination not found.')

    # Use proper encoding
    if isinstance(instruction, unicode):
        instruction = instruction.encode('utf-8')

    # Get arg size
    elems = instruction.split(ELEM_SEP, 1)

    try:
        arg_size = int(elems[0])
    except:
        # Expected ValueError
        raise InvalidInstruction(
            'Invalid arg length. Possibly due to missing element separator!')

    arg_str = elems[1][:arg_size]

    remaining = elems[1][arg_size:]

    args = [arg_str]

    if remaining.startswith(ARG_SEP):
        # Ignore the ARG_SEP to parse next arg.
        remaining = remaining[1:]
    elif remaining == INST_TERM:
        # This was the last arg!
        return args
    else:
        # The remaining is neither starting with ARG_SEP nor INST_TERM.
        raise InvalidInstruction(
            'Instruction arg (%s) has invalid length.' % arg_str)

    next_args = decode_args(remaining)

    if next_args:
        args = args + next_args

    return args


def encode_arg(arg):
    """
    Encode argument to be sent in a valid Guacamole instruction.

    example:
    >> arg = encode_arg('size')
    >> arg == '4.size'
    >> True

    :return: str
    """
    if isinstance(arg, unicode):
        arg_utf8 = arg.encode('utf-8')
    else:
        arg_utf8 = arg

    return ELEM_SEP.join([str(len(str(arg_utf8))), str(arg_utf8)])


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

        args = decode_args(instruction)

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
