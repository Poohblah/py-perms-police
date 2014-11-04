import os
import pwd
import grp

def _getUid(user):
    try:
        result = pwd.getpwnam(user).pw_uid
    except (KeyError, TypeError):
        result = -1
    return result

def _getGid(group):
    try:
        result = grp.getgrnam(group).gr_gid
    except (KeyError, TypeError):
        result = -1
    return result

def update(path,
           user=None,
           group=None,
           add_mode=0,
           rem_mode=0,
           set_mode=0):
    uid = _getUid(user)
    gid = _getGid(group)
    stat = os.stat(path)
    old_mode = stat.st_mode
    if set_mode:
        new_mode = set_mode
    else:
        new_mode = old_mode | add_mode
        new_mode = new_mode ^ (rem_mode & new_mode)
    if ( uid != -1 or gid != -1 ) \
        and ( uid != stat.st_uid or gid != stat.st_gid ):
        os.chown(path, uid, gid)
    if new_mode != old_mode:
        os.chmod(path, new_mode)

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
        self.group        = group
        self.add_perms    = add_perms
        self.remove_perms = remove_perms
        self.ignore_perms = ignore_perms
        if owner is not None:
            self.ignore_owner = False
        else:
            self.ignore_owner = ignore_owner
        if group is not None:
            self.ignore_group = False
        else:
            self.ignore_group = ignore_group

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
        addperms = self.add_perms ^ (self.add_perms & self.ignore_perms)
        newperms = oldperms | addperms
        remperms = self.remove_perms ^ (self.remove_perms & self.ignore_perms)
        newperms = newperms ^ (remperms & newperms)
        if ( self._uid != -1 or self._gid != -1 ) \
            and ( self._uid != stat.st_uid or self._gid != stat.st_gid ):
            os.chown(path, self._uid, self._gid)
        if newperms != oldperms:
            os.chmod(path, newperms)

    # def mergeState(self, state):
    #     if state.owner: self.owner = state.owner
    #     self.ignore_owner = state.ignore_owner
    #     if state.group: self.group = state.group
    #     self.ignore_group = state.ignore_group
    #     self.add_perms = self.add_perms | state.add_perms ^ state.ignore_perms
    #     self.remove_perms = self.remove_perms | state.remove_perms \
    #         ^ state.ignore_perms
    #     self.ignore_perms = state.ignore_perms
