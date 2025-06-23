import re

from pathlib import Path


def comment_out_in_file(filepath, patterns):
    try:
        with open(filepath) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return False
    changed = False
    with open(filepath, 'w') as f:
        for line in lines:
            if any(re.search(pattern, line) for pattern in patterns):
                if not line.strip().startswith('#'):
                    f.write('# ' + line)
                    changed = True
                else:
                    f.write(line)
            else:
                f.write(line)
    return changed


# Patterns to comment out
grpc_patterns = [
    r'import grpc',
    r'from a2a\\.grpc',
    r'import google\\.protobuf',
]
req_patterns = [r'grpcio', r'protobuf']

# Comment out in all .py files
for pyfile in Path('src').rglob('*.py'):
    comment_out_in_file(pyfile, grpc_patterns)
for pyfile in Path('tests').rglob('*.py'):
    comment_out_in_file(pyfile, grpc_patterns)

# Comment out in requirements/pyproject
comment_out_in_file('pyproject.toml', req_patterns)
if Path('requirements.txt').exists():
    comment_out_in_file('requirements.txt', req_patterns)
