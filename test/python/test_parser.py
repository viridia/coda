'''Unit tests for codagen idlparser'''
from coda.compiler import ast, errors, parser
import unittest

from unittest.mock import Mock

class ParserTest(unittest.TestCase):
  def setUp(self):
    self.errorReporter = errors.ErrorReporter()
    self.errorReporter.error = Mock()
    self.errorReporter.showErrorAt = Mock()
    self.errorReporter.showErrorLine = Mock()
    self.parser = parser.Parser(self.errorReporter)

  def testErrorAt(self):
    self.parseError('\n      23\n')
    self.errorReporter.showErrorAt.assert_called_with(
        'dummy.coda', 2, 7, 'Unexpected token: NUMBER')

  def testErrorAt2(self):
    self.parseError('\n\n23\n')
    self.errorReporter.showErrorAt.assert_called_with(
        'dummy.coda', 3, 1, 'Unexpected token: NUMBER')

  def testComment(self):
    self.parse('\n# comment')

  def testUnexpectedEndOfInput(self):
    self.parseError('''
        # comment
        options {''')
    self.errorReporter.error.assert_called_with(
        'Unexpected end of input at line 3')

  def testPackage(self):
    filedesc = self.parse('package foo.bar;')
    self.assertEqual(filedesc.getPackage(), 'foo.bar')

    filedesc = self.parse('package foo . bar ;')
    self.assertEqual(filedesc.getPackage(), 'foo.bar')

  def testMissingPackage(self):
    filedesc = self.parse('''
        options {}''')
    self.assertIsNotNone(filedesc.options)

  def testImports(self):
    filedesc = self.parse('''
      import "a";
      import "b";
      package foo;''')
    self.assertEquals(2, len(filedesc.imports))

  def testEmptyGlobalOptions(self):
    filedesc = self.parse('''
      package foo;

      options {}''')
    self.assertEquals(0, len(filedesc.options))

  def testGlobalOptions(self):
    filedesc = self.parse('''
      package foo;

      options {
        mutable = true;
        package:java = 'strval';
        package:cpp.stl = true;
      }
      ''')
    self.assertIsNotNone(filedesc)
    self.assertEquals(3, len(filedesc.options))

    # Option 0
    self.assertIsNone(filedesc.options[0].scope)
    self.assertEquals(filedesc.options[0].name, 'mutable')
    self.assertIsInstance(filedesc.options[0].value, ast.BooleanValue)
    self.assertEquals(filedesc.options[0].value.value, True)

    # Option 1
    self.assertEquals(filedesc.options[1].scope, 'java')
    self.assertEquals(filedesc.options[1].name, 'package')
    self.assertIsInstance(filedesc.options[1].value, ast.StringValue)
    self.assertEquals(filedesc.options[1].value.value, 'strval')

    # Option 2
    self.assertEquals(filedesc.options[2].scope, 'cpp.stl')
    self.assertEquals(filedesc.options[2].name, 'package')

  def testStringParsing(self):
    filedesc = self.parse('''
      options {
        test1 = 'a\nb';
        test2 = 'a\0b';
      }
      ''')

    self.assertEquals(filedesc.options[0].value.value, 'a\nb')
    self.assertEquals(filedesc.options[1].value.value, 'a\0b')

  def testDefineStruct(self):
    filedesc = self.parse('''
      package foo;

      struct Test {
      }
      ''')
    self.assertEquals(1, len(filedesc.structs))
    struct = filedesc.structs[0]
    self.assertEquals('Test', struct.name)

  def testDefineStructField(self):
    filedesc = self.parse('''
      package foo;

      struct Test {
        data : i32 = 1;
      }
      ''')
    struct = filedesc.structs[0]
    self.assertEquals('Test', struct.name)
    self.assertEquals(1, len(struct.fields))
    self.assertEquals('data', struct.fields[0].name)
    self.assertIsInstance(struct.fields[0].fieldType, ast.TypeName)
    self.assertEquals('i32', struct.fields[0].fieldType.name)

  def testExtensionRange(self):
    filedesc = self.parse('''
      package foo;

      struct Test {
        extensions 100 to 1000;
      }

      struct Test2 {
        extensions 100 to max;
      }
      ''')
    struct = filedesc.structs[0]
    self.assertEquals((100, 1000), struct.getExtensionRange())
    struct = filedesc.structs[1]
    self.assertEquals((100, 2**32-1), struct.getExtensionRange())

  def testDuplicateExtensionRange(self):
    self.parseError('''
      package foo;

      struct Test {
        extensions 100 to 1000;
        extensions 100 to 1001;
      }
      ''')
    self.errorReporter.showErrorAt.assert_called_with(
        'dummy.coda', 6, 9, 'Extension range already defined')

  def testDefineEnum(self):
    filedesc = self.parse('''
      package foo;

      enum Test {
      }
      ''')
    self.assertEquals(1, len(filedesc.enums))
    enum = filedesc.enums[0]
    self.assertEquals('Test', enum.name)

  def testDefineEnumMember(self):
    filedesc = self.parse('''
      package foo;

      enum Test {
        ONE = 1,
        TWO
      }
      ''')
    enum = filedesc.enums[0]
    self.assertEquals(2, len(enum.values))
    self.assertEquals('ONE', enum.values[0].name)
    self.assertEquals('TWO', enum.values[1].name)

  def testDefineExtension(self):
    filedesc = self.parse('''
      package foo;

      extend Test {
      }
      ''')
    self.assertEquals(0, len(filedesc.structs))
    self.assertEquals(1, len(filedesc.extensions))
    ext = filedesc.extensions[0]
    self.assertEquals('Test', ext.extends.name)

  def testDefineExtensionField(self):
    filedesc = self.parse('''
      package foo;

      extend Test {
        data : i32 = 1;
      }
      ''')
    ext = filedesc.extensions[0]
    self.assertEquals('Test', ext.extends.name)
    self.assertEquals(1, len(ext.fields))
    self.assertEquals('data', ext.fields[0].name)
    self.assertIsInstance(ext.fields[0].fieldType, ast.TypeName)
    self.assertEquals('i32', ext.fields[0].fieldType.name)

  def parse(self, source):
    self.errorReporter.error.side_effect = self.mockError
    self.errorReporter.showErrorAt.side_effect = self.mockShowErrorAt
    return self.parser.parse(source, 'dummy.coda')

  def parseError(self, source):
    return self.parser.parse(source, 'dummy.coda')

  def mockError(self, msg):
    self.fail("Unexpected parsing error: " + msg)

  def mockShowErrorAt(self, srcFile, lineno, column, msg):
    self.fail("Unexpected parsing error: " + msg)

if __name__ == "__main__":
    unittest.main()
