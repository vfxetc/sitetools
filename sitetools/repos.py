import os
import re
from collections import Callable
from subprocess import call, check_call, check_output, CalledProcessError

from pkg_resources import iter_entry_points


def git_call(deployed_repo, *args, **kwargs):
    deployed_repo = os.path.abspath(deployed_repo)
    kwargs.setdefault('cwd', os.path.dirname(deployed_repo))
    cmd = ['git', '--git-dir', deployed_repo] 
    cmd.extend(args)
    return check_call(cmd, **kwargs)


def git_output(deployed_repo, *args, **kwargs):
    deployed_repo = os.path.abspath(deployed_repo)
    kwargs.setdefault('cwd', os.path.dirname(deployed_repo))
    cmd = ['git', '--git-dir', deployed_repo] 
    cmd.extend(args)
    return check_output(cmd, **kwargs)


def git_remotes(deployed_repo):
    remotes = {}
    for line in git_output(deployed_repo, 'remote', '-v').splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        remotes[parts[0]] = parts[1]
    return remotes


def git_status_counts(repo):
    counts = {}
    for line in git_output(repo, 'status', '--porcelain').splitlines():
        line = line.strip()
        if not line:
            continue
        status = line.split()[0]
        counts[status] = counts.get(status, 0) + 1
    return counts


def git_rev_parse(deployed_repo, original_name):
        
    name = original_name
    res = None
    visited = set()
    while not res or not re.match(r'^[0-9a-f]{40}$', res):
        
        if res and res.startswith('ref:'):
            name = res[4:].strip()
        
        if name in visited:
            raise ValueError('recursion in refs: %r at %r' % (name, res))
        visited.add(name)
        
        for args in [
            (deployed_repo, name),
            (deployed_repo, 'refs/heads', name),
            (deployed_repo, 'refs/remotes', name),
        ]:
            path = os.path.join(*args)
            if os.path.exists(path):
                res = open(path).read().strip()
                break
        else:
            # warning("Could not directly parse rev %r from %r in %r" % (name, original_name, deployed_repo))
            res = git_output(deployed_repo, 'rev-parse', '--verify', original_name).strip()
    
    return res or None


def git_distance(deployed_repo, left, right):
    try:
        out = git_output(deployed_repo, 'rev-list', '--left-right', '--count', '%s...%s' % (left, right))
    except CalledProcessError:
        return
    m = re.match(r'^\s*(\d+)\s+(\d+)\s*$', out)
    if not m:
        # print colour("WARNING:", bg='yellow', bright=True, reset=True), 'Could not get rev distance from %r to %r in %r' % (left, right, deployed_repo)
        return (0, 0)
    return int(m.group(1)), int(m.group(2))


def iter_available_packages():
    """Return a list of tools that are available to be installed."""

    ks_git = os.environ.get('GIT')
    for name in sorted(os.listdir(ks_git), key=str.lower):
        if name.startswith('.') or not name.endswith('.git'):
            continue
        name = name[:-4]
        yield {
            'name': name,
            'repo': 'git@git.westernx:westernx/%s' % name
        }

