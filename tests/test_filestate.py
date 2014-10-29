import unittest
import mock
import src.filestate
import os

@mock.patch('src.filestate.os', autospec=True)
@mock.patch('src.filestate.pwd', autospec=True)
@mock.patch('src.filestate.grp', autospec=True)
class TestFileState(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testEmptyFileState(self, mock_grp, mock_pwd, mock_os):
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

    def testChown(self, mock_grp, mock_pwd, mock_os):
        # Chown should only be called when the uid/gid will actually change.
        #
        # Chown should be called with the proper uid/gid.

        fn     = "foobar"
        user1  = "alice"
        uid1   = 1001
        group1 = "foo"
        gid1   = 2001
        user2  = "bob"
        uid2   = 1002
        group2 = "bar"
        gid2   = 2002

        # map names to uids/gids using mock to spoof results
        uid_map = {user1: uid1, user2: uid2}
        def get_uid(*args):
            return mock.MagicMock(pw_uid=uid_map[args[0]])

        gid_map = {group1: gid1, group2: gid2}
        def get_gid(*args):
            return mock.MagicMock(gr_gid=gid_map[args[0]])

        mock_pwd.getpwnam = mock.MagicMock(side_effect=get_uid)
        mock_grp.getgrnam = mock.MagicMock(side_effect=get_gid)

        call_list = []

        def run_filestate_chown(olduser, oldgroup, newuser, newgroup):
            stat = mock_os.stat.return_value
            stat.st_mode = 0644
            stat.st_uid = uid_map[olduser]
            stat.st_gid = gid_map[oldgroup]
            fs = src.filestate.FileState(owner=newuser, group=newgroup)
            fs.achieveState(fn)
            if olduser != newuser or oldgroup != newgroup:
                call_list.append(mock.call.os.chown(fn,
                    uid_map[newuser], gid_map[newgroup]))
            self.assertEqual(mock_os.chown.mock_calls, call_list)

        # do not change user or group
        run_filestate_chown(user1, group1, user1, group1)
        # only change user
        run_filestate_chown(user1, group1, user2, group1)
        # only change group
        run_filestate_chown(user2, group1, user2, group2)
        # change both user and group
        run_filestate_chown(user2, group2, user1, group1)

    def testChmod(self, mock_grp, mock_pwd, mock_os):
        # Chmod should only be called if the mode will actually change.

        fn = "/path/to/test/file"
        call_list = []

        def run_filestate_chmod(mode, add_perms, remove_perms, ignore_perms, 
                expected_mode):
            stat = mock_os.stat.return_value
            stat.st_mode = mode
            fs = src.filestate.FileState(add_perms=add_perms,
                remove_perms=remove_perms, ignore_perms=ignore_perms)
            fs.achieveState(fn)
            if mode != expected_mode:
                call_list.append(mock.call.os.chmod(fn, expected_mode))
            self.assertEqual(mock_os.chmod.mock_calls, call_list)

        run_filestate_chmod(0644, 0, 0, 0, 0644)
        run_filestate_chmod(0644, 020, 0, 0, 0664)
        run_filestate_chmod(0644, 0, 04, 0, 0640)
        run_filestate_chmod(0644, 0, 0644, 0, 0)
        run_filestate_chmod(0644, 0131, 0020, 0, 0755)
        run_filestate_chmod(0644, 0131, 0020, 0777, 0644)
        run_filestate_chmod(0755, 02020, 0, 0, 02775)
        run_filestate_chmod(0755, 02775, 0, 0, 02775)
