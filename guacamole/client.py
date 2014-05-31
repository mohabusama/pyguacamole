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

import socket
import select
import logging

from guacamole import logger
from exceptions import GuacamoleError

from instruction import INST_TERM
from instruction import GuacamoleInstruction as Instruction

# supported protocols
PROTOCOLS = ('vnc', 'rdp', 'ssh')

PROTOCOL_NAME = 'guacamole'

BUF_LEN = 4096


class GuacamoleClient(object):
    def __init__(self, host, port, timeout=20, debug=False):
        """
        Guacamole Client class. This class can handle communication with guacd
        server.

        :param host: guacd server host.

        :param port: guacd server port.

        :param timeout: socket connection timeout.

        :param debug: if True, default logger will switch to Debug level.
        """
        self.host = host
        self.port = port
        self.timeout = timeout

        self._client = None

        # handshake established?
        self.connected = False

        # Receiving buffer
        self._buffer = bytearray()

        if debug:
            logger.setLevel(logging.DEBUG)

    @property
    def client(self):
        """
        Socket connection.
        """
        if not self._client:
            self._client = socket.create_connection(
                (self.host, self.port), self.timeout)

        return self._client

    def close(self):
        """
        Terminate connection with Guacamole guacd server.
        """
        self.client.close()
        self._client = None
        self.connected = False

    def receive(self):
        """
        Receives instructions from Guacamole guacd server.
        """
        start = 0

        while True:
            idx = self._buffer.find(INST_TERM, start)
            if idx != -1:
                # instruction was fully received!
                line = str(self._buffer[:idx + 1])
                self._buffer = self._buffer[idx + 1:]
                return line
            else:
                start = len(self._buffer)
                # we are still waiting for instruction termination
                ready, _, _ = select.select([self.client], [], [])
                buf = self.client.recv(BUF_LEN)
                if not buf:
                    # No data recieved, connection lost?!
                    self.close()
                    return None
                self._buffer.extend(buf)

    def send(self, data):
        """
        Send encoded instructions to Guacamole guacd server.
        """
        self.client.sendall(data)

    def read_instruction(self):
        """
        Read and decode instruction.
        """
        return Instruction.load(self.receive())

    def send_instruction(self, instruction):
        """
        Send instruction after encoding.
        """
        return self.send(instruction.encode())

    def handshake(self, protocol='vnc', width=1024, height=768, dpi=96,
                  audio=(), video=(), **kwargs):
        """
        Establish connection with Guacamole guacd server via handshake.
        """
        if protocol not in PROTOCOLS:
            raise GuacamoleError('Cannot start Handshake. Missing protocol.')

        # 1. Send 'select' instruction
        self.send_instruction(Instruction('select', protocol))

        # 2. Receive `args` instruction
        instruction = self.read_instruction()

        if not instruction:
            raise GuacamoleError(
                'Cannot establish Handshake. Connection Lost!')

        if instruction.opcode != 'args':
            raise GuacamoleError(
                'Cannot establish Handshake. Expected opcode `args`, '
                'received `%s` instead.' % instruction.opcode)

        # 3. Respond with size, audio & video support
        self.send_instruction(Instruction('size', width, height, dpi))

        self.send_instruction(Instruction('audio', *audio))
        self.send_instruction(Instruction('video', *video))

        # 4. Send `connect` instruction with proper values
        connection_args = [
            kwargs.get(arg.replace('-', '_'), '') for arg in instruction.args
        ]

        self.send_instruction(Instruction('connect', *connection_args))

        self.connected = True
