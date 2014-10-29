import os
import pwd
import grp

class FileState():

    def __init__(self,
            owner=None,
            ignore_owner=True,
            group=None,
            ignore_group=True,
            add_perms=0,
            remove_perms=0,
            ignore_perms=0
            ):
        self.owner        = owner
        if owner is not None:
            self.ignore_owner = False
        else:
            self.ignore_owner = ignore_owner
        self.group        = group
        if group is not None:
            self.ignore_group = False
        else:
            self.ignore_group = ignore_group
        self.add_perms    = add_perms
        self.remove_perms = remove_perms
        self.ignore_perms = ignore_perms

    def _setUidAndGid(self):
        if self.owner is not None and not self.ignore_owner:
            self._uid = pwd.getpwnam(self.owner).pw_uid
        else:
            self._uid = -1
        if self.group is not None and not self.ignore_group:
            self._gid = grp.getgrnam(self.group).gr_gid
        else:
            self._gid = -1

    def achieveState(self, path):
        self._setUidAndGid()
        stat = os.stat(path)
        oldperms = stat.st_mode
        newperms = ( oldperms \
             | (self.add_perms ^ (self.ignore_perms & self.add_perms)) ) \
             ^ ( self.remove_perms ^ (self.ignore_perms & self.remove_perms) )
        if ( self._uid != -1 or self._gid != -1 ) \
            and ( self._uid != stat.st_uid or self._gid != stat.st_gid ):
            os.chown(path, self._uid, self._gid)
        if newperms != oldperms:
            os.chmod(path, newperms)

    def mergeState(self, state):
        if state.owner: self.owner = state.owner
        self.ignore_owner = state.ignore_owner
        if state.group: self.group = state.group
        self.ignore_group = state.ignore_group
        self.add_perms = self.add_perms | state.add_perms ^ state.ignore_perms
        self.remove_perms = self.remove_perms | state.remove_perms \
            ^ state.ignore_perms
        self.ignore_perms = state.ignore_perms
