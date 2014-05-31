from mock import MagicMock
from unittest import TestCase

from guacamole.client import GuacamoleClient
from guacamole.exceptions import GuacamoleError, InvalidInstruction


class GuacamoleCientTest(TestCase):

    def setUp(self):
        self.client = GuacamoleClient('127.0.0.1', 4822)
        # patch `send`
        self.client.send = MagicMock()

    def test_handshake(self):
        """
        Test successful handshake.
        """
        global step
        step = 0

        def mock_send_instruction_handshake(instruction):
            global step
            if step == 0:
                assert instruction.opcode == 'select'
                step += 1
            elif step == 1:
                assert instruction.opcode == 'size'
                step += 1
            elif step == 4:
                assert instruction.opcode == 'connect'
                step += 1

        # mock and vaidate send_instruction in handshake
        self.client.send_instruction = MagicMock(
            side_effect=mock_send_instruction_handshake)
        # successful `args` response for `select` instruction
        self.client.receive = MagicMock(
            side_effect=['4.args,8.hostname,4.port,6.domain,8.username;'])

        self.client.handshake(protocol='rdp')

        self.assertTrue(self.client.connected)

    def test_handshake_invalid_protocol(self):
        """
        Test invalid handshake.
        """

        with self.assertRaises(GuacamoleError):
            self.client.handshake(protocol='invalid')

    def test_handshake_protocol_failure(self):
        """
        Test invalid protocol instruction.
        """
        # expected `args`
        self.client.receive = MagicMock(
            side_effect=['7.invalid,8.hostname,4.port,6.domain,8.username;'])

        with self.assertRaises(GuacamoleError):
            self.client.handshake(protocol='rdp')

    def test_handshake_invalid_instruction(self):
        """
        Test invalid instruction.
        """
        self.client.receive = MagicMock()
        self.client.receive.return_value = ''

        with self.assertRaises(InvalidInstruction):
            self.client.handshake(protocol='rdp')

    def test_handshake_invalid_instruction_args(self):
        """
        Test invalid instruction.
        """
        # invalid arg length
        self.client.receive = MagicMock()
        self.client.receive.return_value = '5.args;'

        with self.assertRaises(InvalidInstruction):
            self.client.handshake(protocol='rdp')

    def test_handshake_invalid_instruction_termination(self):
        """
        Test invalid instruction.
        """
        # invalid instruction terminator `;`
        self.client.receive = MagicMock(
            side_effect=['4.args,8.hostname,4.port,6.domain,8.username'])

        with self.assertRaises(InvalidInstruction):
            self.client.handshake(protocol='rdp')

