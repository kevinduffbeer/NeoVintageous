# Copyright (C) 2018 The NeoVintageous Team (NeoVintageous).
#
# This file is part of NeoVintageous.
#
# NeoVintageous is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# NeoVintageous is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NeoVintageous.  If not, see <https://www.gnu.org/licenses/>.

from NeoVintageous.tests import unittest


class TestFeedKey(unittest.ViewTestCase):

    def feedkey(self, key):
        self.view.window().run_command('_nv_feed_key', {'key': key})

    def tearDown(self):
        super().tearDown()
        self.resetRegisters()
        self.resetMacros()

    def test_esc(self):
        self.visual('f|izz b|uzz')
        self.feedkey('<esc>')
        self.assertNormal('fizz |buzz')
        self.assertStatusLineIsNormal()

    def test_esc_key_should_be_case_insensitive(self):
        for key in ('<Esc>', '<esc>', '<ESC>'):
            self.visual('f|izz b|uzz')
            self.feedkey(key)
            self.assertNormal('fizz |buzz')

    def test_motion(self):
        self.normal('fi|zz buzz')
        self.feedkey('w')
        self.assertNormal('fizz |buzz')

    def test_count_motion(self):
        self.normal('fi|zz buzz three four')
        self.feedkey('3')
        self.feedkey('w')
        self.assertNormal('fizz buzz three |four')

    def test_visual_motion(self):
        self.visual('f|iz|z buzz')
        self.feedkey('w')
        self.assertVisual('f|izz b|uzz')
        self.assertStatusLineIsVisual()

    def test_zero_is_not_a_count(self):
        self.normal('x\n  fi|zz')
        self.feedkey('0')
        self.assertNormal('x\n|  fizz')

    def test_double_digit_count(self):
        self.normal('|1234567890123456789012345')
        self.feedkey('2')
        self.feedkey('3')
        self.feedkey('l')
        self.assertNormal('12345678901234567890123|45')

    def test_double_digit_count_ending_in_zero(self):
        self.normal('|1234567890123456789012345')
        self.feedkey('2')
        self.feedkey('0')
        self.feedkey('l')
        self.assertNormal('12345678901234567890|12345')

    def test_namespaced_motion(self):
        self.normal('1\n2\nf|izz')
        self.feedkey('g')
        self.assertStatusLineEqual('g')
        self.assertNormal('1\n2\nf|izz')
        self.feedkey('g')
        self.assertNormal('|1\n2\nfizz')
        self.assertStatusLineIsNormal()

    def test_count_namespaced_motion(self):
        self.normal('1\n2\n3\nf|izz')
        self.feedkey('2')
        self.feedkey('g')
        self.assertStatusLineEqual('2g')
        self.assertNormal('1\n2\n3\nf|izz')
        self.feedkey('g')
        self.assertNormal('1\n|2\n3\nfizz')
        self.assertStatusLineIsNormal()

    def test_operator(self):
        self.normal('f|izz')
        self.feedkey('~')
        self.assertNormal('fI|zz')
        self.assertStatusLineIsNormal()

    def test_operator_motion(self):
        self.normal('fi|zz buzz')
        self.feedkey('d')
        self.assertStatusLineEqual('d')
        self.feedkey('w')
        self.assertNormal('fi|buzz')
        self.assertStatusLineIsNormal()

    def test_visual_operator(self):
        self.visual('fi|zz bu|zz')
        self.feedkey('d')
        self.assertNormal('fi|zz')
        self.assertStatusLineIsNormal()
        self.assertRegistersEqual('"-', 'zz bu')
        self.assertRegistersEmpty('01')

    def test_count_operator_motion(self):
        self.normal('fi|zz buzz three four')
        self.feedkey('3')
        self.feedkey('d')
        self.assertStatusLineEqual('3d')
        self.feedkey('w')
        self.assertNormal('fi|four')
        self.assertStatusLineIsNormal()
        self.assertRegistersEqual('"-', 'zz buzz three ')
        self.assertRegistersEmpty('01')

    def test_operator_operator_dd(self):
        self.normal('1\nfi|zz\n2\n3')
        self.feedkey('d')
        self.feedkey('d')
        self.assertNormal('1\n|2\n3')
        self.assertRegistersEqual('"1', 'fizz\n', linewise=True)
        self.assertRegistersEmpty('-02')
        self.assertStatusLineIsNormal()

    def test_operator_operator_cc(self):
        self.normal('1\nfi|zz\n2\n3')
        self.feedkey('c')
        self.feedkey('c')
        self.assertInsert('1\n|\n2\n3')
        self.assertRegistersEqual('"1', 'fizz\n', linewise=True)
        self.assertRegistersEmpty('-02')
        self.assertStatusLineIsInsert()

    def test_operator_operator_equal_equal(self):
        self.settings().set('translate_tabs_to_spaces', True)
        self.settings().set('tab_size', 4)
        self.normal('1\nfi|zz\n2')
        self.feedkey('>')
        self.feedkey('>')
        self.assertNormal('1\n    |fizz\n2')
        self.assertRegistersEmpty('"-012abc')
        self.assertStatusLineIsNormal()

    def test_motion_and_operator_counts_are_multiplied(self):
        self.normal('o|ne two three four five six seven')
        self.feedkey('3')
        self.feedkey('d')
        self.feedkey('2')
        self.assertStatusLineEqual('3d2')
        self.feedkey('w')
        self.assertNormal('o|seven')
        self.assertStatusLineIsNormal()
        self.assertRegistersEqual('"-', 'ne two three four five six ')
        self.assertRegistersEmpty('01')

    def test_register(self):
        self.normal('fi|zz buzz')
        self.feedkey('"')
        self.feedkey('c')
        self.feedkey('d')
        self.assertStatusLineEqual('"cd')
        self.feedkey('w')
        self.assertNormal('fi|buzz')
        self.assertStatusLineIsNormal()
        self.assertRegistersEqual('"-c', 'zz ')
        self.assertRegistersEmpty('012abde')

    @unittest.mock_bell()
    def test_unknown_operator_motion_invokes_bell(self):
        self.normal('fi|zz')
        self.feedkey('d')
        self.feedkey('o')
        self.assertNormal('fi|zz')
        self.assertStatusLineIsNormal()
        self.assertRegistersEmpty('"-012abc')
        self.assertBell()

    def test_malformed_visual_selection_is_auto_corrected_by_feed(self):
        self.normal('fi|zz buzz fizz')
        self.select((2, 7))
        self.feedkey('w')
        self.assertVisual('fi|zz buzz f|izz')

    def test_input_collecting(self):
        self.normal('fi|zz buzz')
        self.feedkey('f')
        self.assertNormal('fi|zz buzz')
        self.assertStatusLineEqual('f')
        self.feedkey('u')
        self.assertNormal('fizz b|uzz')
        self.assertStatusLineIsNormal()

    def test_input_collecting_replace(self):
        self.normal('fi|zz')
        self.feedkey('R')
        self.assertReplace('fi|zz')
        self.assertStatusLineIsReplace()

    def test_record(self):
        self.normal('fi|zz buzz fizz buzz fizz buzz')
        self.feedkey('q')
        self.assertStatusLineEqual('q')
        self.feedkey('n')
        self.assertStatusLineEqual('Recording...')
        self.feedkey('f')
        self.feedkey('b')
        self.feedkey('q')
        self.assertNormal('fizz |buzz fizz buzz fizz buzz')
        self.assertStatusLineEqual('')
        self.feedkey('@')
        self.assertStatusLineEqual('@')
        self.feedkey('n')
        self.assertNormal('fizz buzz fizz |buzz fizz buzz')
        self.assertStatusLineEqual('')
        self.feedkey('@')
        self.assertStatusLineEqual('@')
        self.feedkey('@')
        self.assertNormal('fizz buzz fizz buzz fizz |buzz')
        self.assertStatusLineEqual('')

    def test_record_delete_operation(self):
        self.normal('fizz buzz fizz buzz fizz |buzz')
        self.feedkey('q')
        self.feedkey('x')
        self.assertStatusLineEqual('Recording...')
        self.feedkey('2')
        self.feedkey('d')
        self.feedkey('b')
        self.feedkey('q')
        self.assertNormal('fizz buzz fizz |buzz')
        self.assertStatusLineEqual('')
        self.feedkey('@')
        self.feedkey('x')
        self.assertNormal('fizz |buzz')
        self.assertStatusLineEqual('')

    def test_record_xpos_motion(self):
        self.normal('fi|zz\nbuzz\nfizz\nbuzz\nfizz\nbuzz')
        self.feedkey('q')
        self.feedkey('x')
        self.feedkey('j')
        self.feedkey('q')
        self.assertNormal('fizz\nbu|zz\nfizz\nbuzz\nfizz\nbuzz')
        self.feedkey('@')
        self.feedkey('x')
        self.assertNormal('fizz\nbuzz\nfi|zz\nbuzz\nfizz\nbuzz')
        self.feedkey('2')
        self.feedkey('@')
        self.feedkey('x')
        self.assertNormal('fizz\nbuzz\nfizz\nbuzz\nfi|zz\nbuzz')

    def test_record_xpos_delete_motion_operation(self):
        self.normal('one\n|two\nthree\nfour\nfive\nsix\nseven')
        self.feedkey('q')
        self.feedkey('x')
        self.feedkey('d')
        self.feedkey('j')
        self.feedkey('q')
        self.assertNormal('one\n|four\nfive\nsix\nseven')
        self.feedkey('@')
        self.feedkey('x')
        self.assertNormal('one\n|six\nseven')

    def test_repeat(self):
        self.normal('one |two three four five six seven')
        self.feedkey('d')
        self.feedkey('w')
        self.assertNormal('one |three four five six seven')
        self.feedkey('.')
        self.assertNormal('one |four five six seven')
        self.feedkey('3')
        self.feedkey('.')
        self.assertNormal('one |seven')

    def test_visual_repeat(self):
        self.normal('one |two three four five six seven')
        self.feedkey('v')
        self.feedkey('w')
        self.feedkey('d')
        self.assertNormal('one |hree four five six seven')
        self.feedkey('.')
        self.assertNormal('one |four five six seven')
        self.feedkey('2')
        self.feedkey('.')
        self.assertNormal('one |five six seven')  # visual repeats are ignored in Vim
        self.feedkey('3')
        self.feedkey('.')
        self.assertNormal('one |six seven')  # visual repeats are ignored in Vim

    @unittest.mock_bell()
    def test_trying_to_repeat_normal_mode_commands_in_visual_mode_should_invoke_bell(self):
        self.normal('one |two three four')
        self.feedkey('d')
        self.feedkey('w')
        self.feedkey('v')
        self.feedkey('.')
        self.assertVisual('one |t|hree four')
        self.assertBell()
