import unittest
import mock
import src.filestate
import random
import string
import os

class TestFileState(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('src.filestate.os')
    def testEmptyFileState(self, mock_os):
        # The permissions should stay the same after calling achieveState()
        # on an empty FileState object.

        fn = "foobar"
        stat = mock_os.stat.return_value
        stat.st_mode = 0644

        fs = src.filestate.FileState()
        fs.achieveState(fn)

        self.assertFalse(mock_os.chown.called,
            "chown called though file mode will not change")
        self.assertFalse(mock_os.chmod.called,
            "chmod called though file mode will not change")
