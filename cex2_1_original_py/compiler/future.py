# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: compiler\future.pyc
# Compiled at: 2011-03-08 09:43:14
"""Parser for future statements

"""
from compiler import ast, walk

def is_future(stmt):
    """Return true if statement is a well-formed future statement"""
    if not isinstance(stmt, ast.From):
        return 0
    else:
        if stmt.modname == '__future__':
            return 1
        return 0


class FutureParser:
    features = ('nested_scopes', 'generators', 'division', 'absolute_import', 'with_statement',
                'print_function', 'unicode_literals')

    def __init__(self):
        self.found = {}

    def visitModule(self, node):
        stmt = node.node
        for s in stmt.nodes:
            if not self.check_stmt(s):
                break

    def check_stmt(self, stmt):
        if is_future(stmt):
            for name, asname in stmt.names:
                if name in self.features:
                    self.found[name] = 1
                else:
                    raise SyntaxError, 'future feature %s is not defined' % name

            stmt.valid_future = 1
            return 1
        return 0

    def get_features(self):
        """Return list of features enabled by future statements"""
        return self.found.keys()


class BadFutureParser:
    """Check for invalid future statements"""

    def visitFrom(self, node):
        if hasattr(node, 'valid_future'):
            return
        if node.modname != '__future__':
            return
        raise SyntaxError, 'invalid future statement ' + repr(node)


def find_futures(node):
    p1 = FutureParser()
    p2 = BadFutureParser()
    walk(node, p1)
    walk(node, p2)
    return p1.get_features()


if __name__ == '__main__':
    import sys
    from compiler import parseFile, walk
    for file in sys.argv[1:]:
        print file
        tree = parseFile(file)
        v = FutureParser()
        walk(tree, v)
        print v.found
        print