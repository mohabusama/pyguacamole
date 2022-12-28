"""
The MIT License (MIT)

Copyright (c)   2014 rescale
                2014 - 2016 Mohab Usama
"""
import asyncio
import logging

from guacamole import logger as guac_logger

from guacamole.exceptions import GuacamoleError

from guacamole.instruction import INST_TERM
from guacamole.instruction import GuacamoleInstruction as Instruction

# supported protocols
PROTOCOLS = ('vnc', 'rdp', 'ssh', 'telnet', 'kubernetes')

PROTOCOL_NAME = 'guacamole'

BUF_LEN = 4096


class GuacamoleClient(object):
    """Guacamole Client class."""

    def __init__(self, host, port, timeout=20, debug=False, logger=None):
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

        self._reader = None
        self._writer = None

        # handshake established?
        self.connected = False

        # Receiving buffer
        self._buffer = bytearray()

        # Client ID
        self._id = None

        self.logger = guac_logger
        if logger:
            self.logger = logger

        if debug:
            self.logger.setLevel(logging.DEBUG)

    @property
    def client(self):
        """
        Socket connection.
        """
        if not self._reader and self._writer:
            self._reader, self._writer = asyncio.open_connection(self.host, self.port)
            self.logger.info(f'Client connected with guacd server {self.host} {self.port} {self.timeout}')

        return True

    @property
    def id(self):
        """Return client id"""
        return self._id

    def close(self):
        """
        Terminate connection with Guacamole guacd server.
        """
        self._writer.close()
        await self._writer.wait_closed()
        self.connected = False
        self.logger.info('Connection closed.')

    async def receive(self):
        """
        Receive instructions from Guacamole guacd server.
        """
        start = 0

        while True:
            idx = self._buffer.find(INST_TERM.encode(), start)
            if idx != -1:
                # instruction was fully received!
                line = self._buffer[:idx + 1].decode()
                self._buffer = self._buffer[idx + 1:]
                self.logger.debug('Received instruction: %s' % line)
                return line
            else:
                start = len(self._buffer)
                # we are still waiting for instruction termination
                buf = await self._reader.read(BUF_LEN)
                if not buf:
                    # No data recieved, connection lost?!
                    self.close()
                    msg = 'Connection closed by remote server'
                    self.logger.warn(msg)
                    raise GuacamoleError(msg)

                self._buffer.extend(buf)

    def send(self, data):
        """
        Send encoded instructions to Guacamole guacd server.
        """
        self.logger.debug('Sending data: %s' % data)
        await self._writer.write(data.encode())

    def read_instruction(self):
        """
        Read and decode instruction.
        """
        self.logger.debug('Reading instruction.')
        return Instruction.load(self.receive())

    def send_instruction(self, instruction):
        """
        Send instruction after encoding.
        """
        self.logger.debug('Sending instruction: %s' % str(instruction))
        return self.send(instruction.encode())

    def handshake(self, protocol='vnc', width=1024, height=768, dpi=96,
                  audio=None, video=None, image=None, width_override=None,
                  height_override=None, dpi_override=None, **kwargs):
        """
        Establish connection with Guacamole guacd server via handshake.

        """
        if protocol not in PROTOCOLS and 'connectionid' not in kwargs:
            self.logger.error(
                'Invalid protocol: %s and no connectionid provided' % protocol)
            raise GuacamoleError('Cannot start Handshake. '
                                 'Missing protocol or connectionid.')

        if audio is None:
            audio = list()

        if video is None:
            video = list()

        if image is None:
            image = list()

        # 1. Send 'select' instruction
        self.logger.debug('Send `select` instruction.')

        # if connectionid is provided - connect to existing connectionid
        if 'connectionid' in kwargs:
            self.send_instruction(Instruction('select',
                                              kwargs.get('connectionid')))
        else:
            self.send_instruction(Instruction('select', protocol))

        # 2. Receive `args` instruction
        instruction = self.read_instruction()
        self.logger.debug('Expecting `args` instruction, received: %s'
                          % str(instruction))

        if not instruction:
            self.close()
            raise GuacamoleError(
                'Cannot establish Handshake. Connection Lost!')

        if instruction.opcode != 'args':
            self.close()
            raise GuacamoleError(
                'Cannot establish Handshake. Expected opcode `args`, '
                'received `%s` instead.' % instruction.opcode)
        self.logger.debug(f"ARGS: {instruction}")

        # 3. Respond with size, audio & video support
        self.logger.debug('Send `size` instruction (%s, %s, %s)'
                          % (width, height, dpi))
        self.send_instruction(Instruction('size', width, height, dpi))

        self.logger.debug('Send `audio` instruction (%s)' % audio)
        self.send_instruction(Instruction('audio', *audio))

        self.logger.debug('Send `video` instruction (%s)' % video)
        self.send_instruction(Instruction('video', *video))

        self.logger.debug('Send `image` instruction (%s)' % image)
        self.send_instruction(Instruction('image', *image))

        if timezone := kwargs.get("timezone", None):
            self.logger.debug('Send `timezone` instruction (%s)' % timezone)
            self.send_instruction(Instruction('timezone', timezone))

        if width_override:
            kwargs["width"] = width_override
        if height_override:
            kwargs["height"] = height_override
        if dpi_override:
            kwargs["dpi"] = dpi_override

        # 4. Send `connect` instruction with proper values
        self.logger.debug(instruction.args)
        connection_args = [
            kwargs.get(arg.replace('-', '_'), '') for arg in instruction.args
        ]

        self.logger.debug(f'Send `connect` instruction ({connection_args}')
        self.send_instruction(Instruction('connect', *connection_args))

        # 5. Receive ``ready`` instruction, with client ID.
        instruction = self.read_instruction()
        self.logger.debug(f'Expecting `ready` instruction, received: {instruction}')

        if instruction.opcode != 'ready':
            self.logger.warning(f'Expected `ready` instruction, received: {instruction} instead')

        if instruction.args:
            self._id = instruction.args[0]
            self.logger.debug(
                'Established connection with client id: %s' % self.id)

        self.logger.debug('Handshake completed.')
        self.connected = True
