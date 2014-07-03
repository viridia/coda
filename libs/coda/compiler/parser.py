'''Parser for CODA IDL files.'''

import ply.lex as lex
import ply.yacc as yacc
from coda.compiler import ast, errors

__all__ = [ 'Lexer', 'Parser' ]

# ============================================================================
# Lexer
# ============================================================================

class Lexer:
  '''Lexer for CODA IDL files.'''

  states = (
     ('sstring','exclusive'),
     ('dstring','exclusive'),
   )

  keywords = {
    # Reserved words
    'import': 'IMPORT',
    'public': 'PUBLIC',
    'struct': 'STRUCT',
    'enum': 'ENUM',
    'options': 'OPTIONS',
    'package': 'PACKAGE',
    'extensions': 'EXTENSIONS',
    'extend': 'EXTEND',
    'to': 'TO',
    'max': 'MAX',
    'const': 'CONST',
    'shared': 'SHARED',

    # Named values
    'true': 'TRUE',
    'false': 'FALSE',
  }

  tokens = (
    'RETURNS',
    'EQUALS',
    'SEMI',
    'COLON',
    'COMMA',
    'DOT',
    'LBRACKET',
    'RBRACKET',
    'LBRACE',
    'RBRACE',
    'LPAREN',
    'RPAREN',
    'NUMBER',
    'STRING',
    'ID',
  ) + tuple(keywords.values())

  # Regular expression rules for simple tokens
  t_RETURNS = r'->'
  t_EQUALS = r'='
  t_COLON = r':'
  t_SEMI = r';'
  t_COMMA = r','
  t_DOT = r'\.'
  t_LBRACKET = r'\['
  t_RBRACKET = r'\]'
  t_LBRACE = r'\{'
  t_RBRACE = r'\}'
  t_LPAREN = r'\('
  t_RPAREN = r'\)'

  def t_NUMBER(self, t):
    r'\d+'
#     t.value = int(t.value)
    return t

  def t_ID(self, t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = Lexer.keywords.get(t.value, 'ID')
    return t

  # Track line numbers
  def t_newline(self, t):
    r'\n+'
    self.lexer.lineno += len(t.value)

  # Comment (ignore)
  def t_comment(self, t):
    r'\#.*'

  # Ignore spaces and tabs
  t_ignore = ' \t'
  t_sstring_dstring_ignore = ''

  # Strings

  # Start a quoted string
  def t_quote(self, t):
    '\'|"'
    self.stringVal = []
    self.stringTok = t
    if t.value == '\'':
      self.lexer.begin('sstring')
    else:
      self.lexer.begin('dstring')

  # End of a string if it matches the correct quote type
  def t_sstring_STRING(self, t):
    r"'"
    self.lexer.begin('INITIAL')
    t.value = ''.join(self.stringVal)
    return t

  def t_dstring_STRING(self, t):
    r'"'
    self.lexer.begin('INITIAL')
    t.value = ''.join(self.stringVal)
    return t

  # Regular string characters
  def t_sstring_char(self, t):
    r'[^\\\']+'
    self.stringVal.append(t.value)

  def t_dstring_char(self, t):
    r'[^\\"]+'
    self.stringVal.append(t.value)

  # Escape sequences in strings
  def t_sstring_dstring_backslash(self, t):
    r'\\\\'
    self.stringVal.append('\\')

  def t_sstring_dstring_nl(self, t):
    r'\\n'
    self.stringVal.append('\n')

  def t_sstring_dstring_cr(self, t):
    r'\\r'
    self.stringVal.append('\r')

  def t_sstring_dstring_tab(self, t):
    r'\\t'
    self.stringVal.append('\t')

  # Error handling

  def t_error(self, t):
    self.errorAt(t, "Illegal character '%s'" % t.value[0])
    self.errorReporter.abort();
#     t.lexer.skip(1)

  def t_sstring_dstring_error(self, t):
    self.errorAt(t, "Illegal character '%s'" % t.value[0])
    self.errorReporter.abort();

  # Build the lexer
  def __init__(self, errorReporter, **kwargs):
    self.errorReporter = errorReporter
    self.lexer = lex.lex(module=self, **kwargs)
    self.stringTok = None
    self.stringVal = []

  def token(self):
    return self.lexer.token()

  def input(self, strm):
    self.lexer.input(strm)

  def error(self, msg):
    self.errorReporter.error(msg)

  def errorAt(self, token, msg):
    self.errorReporter.errorAt(
        errors.Location.fromToken(self.sourcePath, token), msg)

# ============================================================================
# Parser
# ============================================================================

class Parser:
  '''Parser for CODA IDL files.'''
  tokens = Lexer.tokens

  def __init__(self, errorReporter):
    self.errorReporter = errorReporter
    self.lexer = Lexer(errorReporter)
    self.parser = yacc.yacc(module=self, write_tables=0, debug=False)
#     self.parser = yacc.yacc(module=self)

  # A module
  def p_file(self, p):
    'file : import_list package_decl options decl_list'
    p[0] = ast.File(self.sourcePath, package=p[2])
    assert p[4] is not None
    p[0].imports += p[1]
    p[0].options += p[3]
    for m in p[4]:
      p[0].addMember(m)

  # Imports
  def p_import_list(self, p):
    '''import_list : import_list import
                   | empty'''
    if len(p) == 3:
      p[0] = p[1] + [p[2]]
    else:
      p[0] = []

  def p_import(self, p):
    '''import : IMPORT PUBLIC STRING SEMI
              | IMPORT STRING SEMI
              | IMPORT STRING'''
    if len(p) == 5:
      p[0] = (True, p[3])
    elif len(p) == 3:
      self.errorAt(p, 1, 'Missing semicolon after import statement')
      p[0] = (False, p[2])
    else:
      p[0] = (False, p[2])

  # Package declaration
  def p_package_decl(self, p):
    '''package_decl : PACKAGE dotted_id SEMI
                    | empty'''
    if len(p) > 2:
      p[0] = p[2].value

  # List of declarations
  def p_options(self, p):
    '''options : OPTIONS LBRACE option_list RBRACE
               | empty'''
    if len(p) == 5:
      p[0] = p[3]
    else:
      p[0] = []

  def p_option_list(self, p):
    '''option_list : option_list option SEMI
                   | empty'''
    if len(p) == 4:
      p[0] = p[1] + [p[2]]
    else:
      p[0] = []

  def p_option(self, p):
    '''option : id COLON dotted_id EQUALS value
              | id EQUALS value'''
    if len(p) == 6:
      p[0] = ast.Option(p[1].location, p[1].value, p[3].value, p[5])
    else:
      p[0] = ast.Option(p[1].location, p[1].value, None, p[3])

  # List of declarations
  def p_decl_list(self, p):
    '''decl_list : decl_list decl
                 | empty'''
    if len(p) == 3:
      p[0] = p[1] + [p[2]]
    else:
      p[0] = []

  # A declaration
  def p_decl(self, p):
    '''decl : struct_decl
            | enum_decl
            | extension_decl'''
    p[0] = p[1]

  def p_struct_decl(self, p):
    'struct_decl : struct_header LBRACE options struct_member_list RBRACE'
    p[0] = p[1]
    p[0].options = p[3]
    for m in p[4]:
      if isinstance(m, tuple):
        minExt, maxExt, location = m
        if p[0].getExtensionRange() != (0, 0):
          self.errorReporter.errorAt(
              location, 'Extension range already defined')
        else:
          p[0].setExtensionRange((minExt, maxExt))
      else:
        p[0].addMember(m)

  def p_struct_header(self, p):
    '''struct_header : STRUCT ID subtype_decl'''
    p[0] = ast.StructDef(self.location(p, 2), p[2])
    p[0].baseType, p[0].typeId = p[3]

  def p_subtype_decl(self, p):
    '''subtype_decl : LPAREN typename RPAREN EQUALS NUMBER
                    | LPAREN typename RPAREN EQUALS dotted_id
                    | LPAREN typename RPAREN
                    | EQUALS NUMBER
                    | EQUALS dotted_id
                    | empty'''
    if len(p) == 6:
      p[0] = p[2], p[5]
    elif len(p) == 4:
      self.errorAt(p, 4, 'Missing subtype ID')
    elif len(p) == 3:
      p[0] = None, p[2]
    else:
      p[0] = None, None

  def p_struct_member_list(self, p):
    '''struct_member_list : struct_member_list struct_member
                          | struct_member_list struct_extensions
                          | empty'''
    if len(p) == 3:
      p[0] = p[1] + [p[2]]
    else:
      p[0] = []

  def p_struct_member(self, p):
    '''struct_member : field
                     | method
                     | struct_decl
                     | enum_decl
                     | extension_decl'''
    p[0] = p[1]

  def p_struct_extensions(self, p):
    '''struct_extensions : EXTENSIONS const_int TO const_int SEMI
                         | EXTENSIONS const_int TO max_field_id SEMI'''
    p[0] = (p[2].value, p[4].value, self.location(p, 1))

  def p_field(self, p):
    '''field : field_name COLON typeref EQUALS NUMBER field_options SEMI'''
    p[0] = ast.StructDef.Field(p[1].location, p[1].value, p[3], int(p[5]))
    p[0].options = p[6]

  def p_field_name(self, p):
    '''field_name : ID
                  | STRING'''
    p[0] = ast.Ident(self.location(p, 1), p[1])

  def p_field_options(self, p):
    '''field_options : LBRACKET field_option_list RBRACKET
                     | empty'''
    if len(p) == 4:
      p[0] = p[2]
    else:
      p[0] = []

  def p_field_option_list(self, p):
    '''field_option_list : field_option_list COMMA field_option
                         | field_option'''
    if len(p) == 4:
      p[0] = p[1] + [p[3]]
    else:
      p[0] = [p[1]]

  def p_field_option(self, p):
    '''field_option : option
                    | id'''
    if isinstance(p[1], ast.Option):
      p[0] = p[1]
    else:
      p[0] = ast.Option(p[1].location, p[1].value, None,
          ast.BooleanValue(p[1].location, True))

  def p_method(self, p):
    '''method : field_name COLON method_params RETURNS typeref EQUALS NUMBER field_options SEMI'''
    p[0] = ast.StructDef.Method(p[1].location, p[1].value, p[3], p[5], p[7])
    p[0].options = p[8]

  def p_method_params(self, p):
    '''method_params : LPAREN param_list RPAREN
                     | empty'''
    if len(p) == 4:
      p[0] = p[2]
    else:
      p[0] = ()

  def p_param_list(self, p):
    '''param_list : param_list COMMA param
                  | param
                  | empty'''
    if len(p) == 4:
      p[0] = p[1] + (p[3],)
    elif p[1] is not None:
      p[0] = (p[1],)
    else:
      p[0] = ()

  def p_param(self, p):
    'param : id COLON typeref'
    p[0] = ast.Param(p[1].location, p[1], p[3])

  def p_enum_decl(self, p):
    'enum_decl : ENUM ID LBRACE enum_value_list RBRACE'
    p[0] = ast.EnumDef(self.location(p, 2), p[2])
    p[0].addValues(p[4])

  def p_enum_value_list(self, p):
    '''enum_value_list : enum_value_list enum_value
                       | empty'''
    if len(p) == 3:
      p[0] = p[1] + [p[2]]
    else:
      p[0] = []

  def p_enum_value(self, p):
    '''enum_value : ID EQUALS const_int SEMI
                  | ID EQUALS const_int COMMA
                  | ID SEMI
                  | ID COMMA
                  | ID'''
    value = None
    if len(p) == 5:
      value = p[3]
    p[0] = ast.EnumDef.Value(self.location(p, 1), p[1], value)

  def p_extension_decl(self, p):
    'extension_decl : EXTEND typename LBRACE struct_member_list RBRACE'
    p[0] = ast.StructDef(self.location(p, 1), p[2])
    p[0].extends = p[2]
    p[0].fields = p[4]

  def p_typeref(self, p):
    '''typeref : modified_typeref
               | typename LBRACKET typeargs RBRACKET
               | typename'''
    if len(p) == 5:
      p[0] = ast.SpecializedType(p[1], p[3])
    else:
      p[0] = p[1]

  def p_modified_typeref(self, p):
    '''modified_typeref : CONST typeref
                        | SHARED typeref'''
    if isinstance(p[2], ast.ModifiedType):
      p[0] = p[2]
    else:
      p[0] = ast.ModifiedType(p[2])
    if p[1] == 'const':
      p[0].const = True
    else:
      p[0].shared = True

  def p_typeargs(self, p):
    '''typeargs : typeargs COMMA typeref
                | typeref'''
    if len(p) > 2:
      p[0] = p[1] + [p[3]]
    else:
      p[0] = [p[1]]

  def p_typename(self, p):
    '''typename : dotted_id'''
    p[0] = ast.TypeName(p[1].location, p[1].value)

  def p_value_list(self, p):
    '''value_list : value_list value
                  | empty'''
    if len(p) == 3:
      p[0] = p[1] + [p[2]]
    else:
      p[0] = []

  def p_value(self, p):
    '''value : const_bool
             | const_int
             | const_string
             | const_list'''
    p[0] = p[1]

  def p_const_int(self, p):
    '''const_int : NUMBER'''
    p[0] = ast.IntegerValue(self.location(p, 1), int(p[1]))

  def p_const_bool(self, p):
    '''const_bool : TRUE
                  | FALSE'''
    if p[1] == 'true':
      p[0] = ast.BooleanValue(self.location(p, 1), True)
    else:
      p[0] = ast.BooleanValue(self.location(p, 1), False)

  def p_const_string(self, p):
    '''const_string : STRING'''
    p[0] = ast.StringValue(self.location(p, 1), p[1])

  def p_const_list(self, p):
    '''const_list : LBRACKET value_list RBRACKET'''
    p[0] = ast.ListValue(self.location(p, 1), p[2])

  def p_max_field_id(self, p):
    '''max_field_id : MAX'''
    p[0] = ast.IntegerValue(self.location(p, 1), 2**32-1)

  def p_dotted_id(self, p):
    '''dotted_id : dotted_id DOT id
                 | id'''
    if len(p) == 4:
      p[0] = ast.Ident(p[1].location, p[1].value + '.' + p[3].value)
    else:
      p[0] = p[1]

  def p_id(self, p):
    '''id : ID
          | PACKAGE
          | CONST
          | SHARED'''
    p[0] = ast.Ident(self.location(p, 1), p[1])

  def p_empty(self, p):
    '''empty :'''

  # Error rule for syntax errors
  def p_error(self, tok):
    if tok:
      tok.lexer = self.lexer.lexer
      self.errorReporter.errorAt(
          errors.Location.fromToken(self.sourcePath, tok),
          "Unexpected token: " + tok.type)
    else:
      self.error("Unexpected end of input at line {0}".format(
          self.lexer.lexer.lineno))

  def parse(self, istream, sourcePath):
    self.sourcePath = sourcePath
    self.lexer.sourcePath = sourcePath
    self.lexer.lexer.lineno = 1
    return self.parser.parse(istream, lexer=self.lexer)

  def error(self, msg):
    self.errorReporter.error(msg)

  def errorAt(self, p, index, msg):
    self.errorReporter.errorAt(self.location(p, index), msg)

  def location(self, p, index):
    return errors.Location(self.sourcePath, self.lexer.lexer.lexdata,
        p.lineno(index), p.lexpos(index))

  def setStart(self, state):
    self.parser.set_start(state)
