import os
import sys
import warnings


def _process_pth(paths, base, file_name):
    """Process a ``.pth`` file similar to site.addpackage(...)."""
    for line in open(os.path.join(base, file_name)):
        line = line.strip()
        if line.startswith('#'):
            continue
        if line.startswith('import'):
            exec line
            continue
        dir_name = os.path.abspath(os.path.join(base, line))
        paths.append(dir_name)


def add_site_dir(dir_name, before=None):
    """Add a pseudo site-packages directory to :data:`python:sys.path`.
    
    :param str dir_name: The directory to add.
    :param str before: A directory on :data:`sys.path` that new paths should be
    inserted before.
    
    Looks for ``.pth`` files at the top-level and ``__site__.pth`` files within
    top-level directories.
    
    """
    
    # Don't so anything if the folder doesn't exist.
    if not os.path.exists(dir_name):
        return
    paths = [dir_name]
    
    # Determine where we want to insert new paths.
    try:
        insert_at = sys.path.index(before) if before else None
    except ValueError:
        insert_at = None
        warnings.warn('%r was not found on sys.path' % before)

    # Process *.pth files in a manner similar to site.addsitedir(...).
    for file_name in os.listdir(dir_name):
    
        # Skip dotfiles.
        if file_name.startswith('.'):
            continue
    
        # *.pth files.
        if file_name.endswith('.pth'):
            _process_pth(paths, dir_name, file_name)
    
        # __site__.pth files inside packages.
        if os.path.exists(os.path.join(dir_name, file_name, '__site__.pth')):
            _process_pth(paths, os.path.join(dir_name, file_name), '__site__.pth')
    
    # Add everything which exists to the path before the path we were asked to.
    existing = set(sys.path)
        
    for path in paths:
        path = os.path.abspath(path)
        
        # Don't add it if this path is already on the sys.path.
        if path in existing:
            continue
        existing.add(path)
        
        # It has to exist.
        if not os.path.exists(path):
            continue
        
        # Put it in the right place.
        if insert_at:
            sys.path.insert(insert_at, path)
            insert_at += 1
        else:
            sys.path.append(path)
        
