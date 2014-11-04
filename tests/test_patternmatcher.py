import unittest
import src.patternmatcher

class TestMatches(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testMatches(self):

        def run_matches(path, pattern, expected_result):
            actual_result = src.patternmatcher.matches(path, pattern)
            msg = """pattermatcher.matches did not return expected result:
path: %s
pattern: %s
expected result: %s
actual result: %s""" % (path, pattern, \
                expected_result, actual_result)
            self.assertEqual(expected_result, actual_result, msg)

        run_matches("/", "/", True)
        run_matches("/foo", "/", False)
        run_matches("/foo/bar", "/foo/bar", True)
        run_matches("/foo/bar", "/baz/bar", False)
        run_matches("/foo/bar", "/foo/*", True)
        run_matches("/foo/bar", "/baz/*", False)
        run_matches("/foo/bar", "/foo/**", True)
        run_matches("/foo/bar", "/baz/**", False)
        run_matches("/foo/bar", "/**/*", True)
        run_matches("/foo/bar", "/foo/**/*", False)
        run_matches("/foo/bar", "/foo/{bar,baz,biz}", True)
        run_matches("/foo/bar", "/foo/{barf,baz,biz}", False)
        run_matches("/foo/bar", "/*/{bar,baz,biz}", True)
        run_matches("/foo/bar", "/*/{barf,baz,biz}", False)
        run_matches("/foo/bar", "/**/{bar,baz,biz}", True)
        run_matches("/foo/bar", "/**/{barf,baz,biz}", False)
        run_matches("/foo/bar", "/foo/{bar*,baz,biz}", True)
        run_matches("/foo/bar", "/foo/{barf*,baz,biz}", False)
