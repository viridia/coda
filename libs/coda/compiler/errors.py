# Defines the standard error reporting mechanism

import sys

# ============================================================================
# Source locations
# ============================================================================

class ErrorPos:
  '''The position of an error within a source file.'''
  def __init__(self, srcFile, lineno, column, lineText):
    self.srcFile = srcFile
    self.lineno = lineno
    self.column = column
    self.lineText = lineText

class Location:
  '''The location of a token within a source file.'''
  def __init__(self, srcFile, srcText, lineno, lexpos):
    self.srcFile = srcFile
    self.srcText = srcText
    self.lineno = lineno
    self.lexpos = lexpos

  @staticmethod
  def fromToken(srcFile, tok):
    return Location(srcFile, tok.lexer.lexdata, tok.lineno, tok.lexpos)

  def getErrorPos(self):
    lineno = self.lineno - 1
    lines = self.srcText.splitlines(True)
    if lineno >= len(lines):
      print(self.srcFile, len(lines), lineno)
    assert len(lines) > lineno
    if lineno < 0:
      lineno = 0
    lineStartPos = sum(len(line) for line in lines[:lineno])
    startCol = self.lexpos - lineStartPos
    if startCol < 0:
      print(self.srcFile, self.lineno, self.lexpos, lineStartPos)
    assert startCol >= 0
    lineText = None
    if lineno >= 0 and lineno < len(lines):
      lineText = lines[lineno][:-1]
    return ErrorPos(self.srcFile, self.lineno, startCol + 1, lineText)

# ============================================================================
# Error reporter
# ============================================================================

class ErrorReporter:
  '''Class that handles error reporting.'''
  def __init__(self):
    self.errorCount = 0

  def error(self, msg):
    '''A general error with no specific location.'''
    sys.stderr.write(msg + '\n')
    self.errorCount += 1
    self.checkErrorLimit()

  def errorAt(self, location, msg):
    '''Report an error that occurs at a specific location within a file.'''
    pos = location.getErrorPos()
    self.showErrorAt(pos.srcFile, pos.lineno, pos.column, msg)
    if pos.lineText:
      self.showErrorLine(pos.lineText, pos.column)
    self.errorCount += 1
    self.checkErrorLimit()

  def showErrorAt(self, srcFile, lineno, column, msg):
    sys.stderr.write("{0}:{1}:{2}: {3}\n".format(srcFile, lineno, column, msg))

  def showErrorLine(self, lineText, column):
    sys.stderr.write("{0}\n".format(lineText))
    sys.stderr.write("{0}^\n".format(' ' * (column - 1)))

  def getErrorCount(self):
    return self.errorCount

  def checkErrorLimit(self):
    if self.errorCount > 8:
      sys.stderr.write("Maximum error limit reached\n")
      sys.exit(-1)

  def abort(self):
    sys.exit(-1)
