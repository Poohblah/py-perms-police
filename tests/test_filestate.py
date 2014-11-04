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
            user = args[0]
            if not user: raise TypeError
            if user not in uid_map: raise KeyError
            return mock.MagicMock(pw_uid=uid_map[user])

        gid_map = {group1: gid1, group2: gid2}
        def get_gid(*args):
            group = args[0]
            if not group: raise TypeError
            if group not in gid_map: raise KeyError
            return mock.MagicMock(gr_gid=gid_map[group])

        mock_pwd.getpwnam = mock.MagicMock(side_effect=get_uid)
        mock_grp.getgrnam = mock.MagicMock(side_effect=get_gid)

        call_list = []

        # spoof file mode
        stat = mock_os.stat.return_value
        stat.st_mode = 0644

        # test update() with no arguments; should do nothing
        src.filestate.update(fn)
        self.assertFalse(mock_os.chown.called,
            "chown called though file mode will not change")

        # test update() with variety of user/group arguments
        def run_filestate_chown(olduser, oldgroup, newuser, newgroup):
            stat.st_uid = uid_map[olduser]
            stat.st_gid = gid_map[oldgroup]
            src.filestate.update(fn, user=newuser, group=newgroup)
            if olduser != newuser or oldgroup != newgroup:
                call_list.append(mock.call.os.chown(fn,
                    uid_map[newuser], gid_map[newgroup]))
            self.assertEqual(mock_os.chown.mock_calls, call_list,
                "chown operation failed")

        run_filestate_chown(user1, group1, user1, group1)
        run_filestate_chown(user1, group1, user2, group1)
        run_filestate_chown(user1, group1, user1, group2)
        run_filestate_chown(user1, group1, user2, group2)

    def testChmod(self, mock_grp, mock_pwd, mock_os):
        # Chmod should only be called if the mode will actually change.

        fn = "/path/to/test/file"

        # spoof file mode
        stat = mock_os.stat.return_value
        stat.st_mode = 0644

        # test update() with no arguments; should do nothing
        src.filestate.update(fn)
        self.assertFalse(mock_os.chmod.called,
            "chmod called though file mode will not change")

        def run_filestate_chmod(mode, add_mode, rem_mode, set_mode, 
                expected_mode):
            call_list = []

            stat = mock_os.stat.return_value
            stat.st_mode = mode

            # reset mock_calls so we can accurately tell what was called
            mock_os.chmod.mock_calls = []

            src.filestate.update(fn, add_mode=add_mode,
                rem_mode=rem_mode, set_mode=set_mode)
            if mode != expected_mode:
                call_list.append(mock.call.os.chmod(fn, expected_mode))

            if mock_os.chmod.mock_calls:
                actual_mode = mock_os.chmod.mock_calls[-1][1][1]
            else:
                actual_mode = mode
            err_msg = "chmod operation failed: start mode: %o, add mode: %o, \
remove mode: %o, set mode: %o, expected result: %o, actual result: %o" \
                % (mode, add_mode, rem_mode, set_mode, expected_mode, \
                    actual_mode)
            self.assertEqual(mock_os.chmod.mock_calls, call_list, err_msg)

        run_filestate_chmod(0644,  0,     0,     0,     0644 )
        run_filestate_chmod(0644,  020,   0,     0,     0664 )
        run_filestate_chmod(0644,  0,     04,    0,     0640 )
        run_filestate_chmod(0644,  0,     0644,  0,     0    )
        run_filestate_chmod(0644,  0131,  0020,  0,     0755 )
        run_filestate_chmod(0644,  0,     0,     0600,  0600 )
        run_filestate_chmod(0644,  0131,  0020,  0777,  0777 )
        run_filestate_chmod(0755,  02020, 0,     0,     02775)
        run_filestate_chmod(0755,  02775, 0,     0,     02775)
        run_filestate_chmod(0755,  0,     0777,  0,     0    )
