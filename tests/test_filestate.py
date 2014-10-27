import unittest
import src.filestate
import os
from pyfakefs import fake_filesystem_unittest

class TestFileState(fake_filesystem_unittest.TestCase):

    def getFileStat(self, path):
        stat  = os.lstat(path)
        owner = stat.st_uid
        group = stat.st_gid
        perms = stat.st_mode
        return {'owner': owner,
                'group': group,
                'perms': perms}

    def createEmptyFile(self, path):
        basedir = os.path.dirname(path)
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        open(path, 'a').close()

    def setUp(self):
        self.setUpPyfakefs()

    def tearDown(self):
        self.tearDownPyfakefs()

    def testEmptyFileState(self):
        """
        The permissions should stay the same after calling achieveState()
        on an empty FileState object.
        """
        tmpf = '/tmp/foo'
        self.createEmptyFile(tmpf)
        oldstat = self.getFileStat(tmpf)
        fs = src.filestate.FileState()
        fs.achieveState(tmpf)
        newstat = self.getFileStat(tmpf)
        self.assertEquals(oldstat, newstat)
