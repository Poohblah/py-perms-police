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
