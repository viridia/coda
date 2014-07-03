// ============================================================================
// Coda text format dcoder
// ============================================================================

#include "coda/io/textdecoder.h"
#include "coda/runtime/typeregistry.h"

#include <strstream>
#include <assert.h>

#include <iostream>

namespace coda {
namespace io {

namespace {

bool isNameStartChar(char ch) {
  return (ch >= 'a' && ch <= 'z') ||
      (ch >= 'A' && ch <= 'Z') ||
      (ch == '_');
}

bool isNameChar(char ch) {
  return (ch >= 'a' && ch <= 'z') ||
      (ch >= 'A' && ch <= 'Z') ||
      (ch >= '0' && ch <= '9') ||
      (ch == '_');
}

bool isDigitChar(char ch) {
  return (ch >= '0' && ch <= '9');
}

bool isHexDigitChar(char ch) {
  return ((ch >= '0' && ch <= '9') || (ch >= 'a' && ch <= 'f') || (ch >= 'A' && ch <= 'F'));
}

}

using namespace coda::descriptors;

runtime::Object* TextDecoder::readObject(const StructDescriptor* desc) {
  return readStructFields(desc, 0);
}

void TextDecoder::readValue(const Type* expectedType, int flags, void* data) {
  int32_t expectedTypeId = expectedType->typeId();
  if (match(TOKEN_LBRACE)) {
    if (token == TOKEN_ID || token == TOKEN_TYPEREF) {
      runtime::Object* v =
          readStructValue(static_cast<const StructDescriptor*>(expectedType), flags);
      expectedType->put(data, &v);
    } else {
      return readMapValue(static_cast<const MapType*>(expectedType), flags, data);
    }
  } else if (match(TOKEN_LBRACKET)) {
    // It's a list literal
    if (expectedType->typeId() != TYPE_KIND_LIST and expectedType->typeId() != TYPE_KIND_SET) {
      typeError(tokenLineno, tokenColumn, expectedType, "list");
    }
    readListValue(expectedType, flags, data);
  } else if (token == TOKEN_INTVAL) {
    switch (expectedTypeId) {
      case TYPE_KIND_INTEGER: {
        const IntegerType* intType = static_cast<const IntegerType*>(expectedType);
        if (intType->getBits() == 16) {
          int16_t v = strtol(tokenValue.c_str(), NULL, 10);
          expectedType->put(data, &v);
        } else if (intType->getBits() == 32) {
          int32_t v = strtol(tokenValue.c_str(), NULL, 10);
          expectedType->put(data, &v);
        } else if (intType->getBits() == 64) {
          int64_t v = strtoll(tokenValue.c_str(), NULL, 10);
          expectedType->put(data, &v);
        }
        break;
      }
      case TYPE_KIND_FLOAT: {
        float v = strtod(tokenValue.c_str(), NULL);
        expectedType->put(data, &v);
        break;
      }
      case TYPE_KIND_DOUBLE: {
        double v = strtod(tokenValue.c_str(), NULL);
        expectedType->put(data, &v);
        break;
      }
      default:
        typeError(tokenLineno, tokenColumn, expectedType, "integer");
        break;
    }
    next();
  } else if (token == TOKEN_FLOATVAL) {
    switch (expectedTypeId) {
      case TYPE_KIND_FLOAT: {
        float v = strtod(tokenValue.c_str(), NULL);
        expectedType->put(data, &v);
        break;
      }
      case TYPE_KIND_DOUBLE: {
        double v = strtod(tokenValue.c_str(), NULL);
        expectedType->put(data, &v);
        break;
      }
      default:
        typeError(tokenLineno, tokenColumn, expectedType, "float");
        break;
    }
    next();
  } else if (token == TOKEN_TRUE or token == TOKEN_FALSE) {
    if (expectedType->typeId() != TYPE_KIND_BOOL) {
      typeError(tokenLineno, tokenColumn, expectedType, "boolean");
    }
    bool v = (token == TOKEN_TRUE);
    expectedType->put(data, &v);
    next();
  } else if (token == TOKEN_STRING) {
    if (expectedType->typeId() != TYPE_KIND_STRING) {
      typeError(tokenLineno, tokenColumn, expectedType, "string");
    }
    expectedType->put(data, &tokenValue);
    next();
  } else if (token == TOKEN_NULL) {
    if (!(flags & TM_NULLABLE)) {
      parseError(tokenLineno, tokenColumn, "Null object ref not allowed here.");
    } else {
      runtime::Object* v = NULL;
      expectedType->put(data, &v);
      next();
    }
  } else if (token == TOKEN_OBJREF) {
    if (!(flags & TM_SHARED)) {
      parseError(tokenLineno, tokenColumn, "Reading shared object into non-shared field.");
    }
    int32_t index = strtol(tokenValue.c_str(), NULL, 10);
    runtime::Object* value = getShared(index);
    if (value == NULL) {
      parseError(tokenLineno, tokenColumn, "Invalid shared object ID " + tokenValue);
    } else if (!value->isInstanceOf(static_cast<const StructDescriptor*>(expectedType))) {
      typeError(tokenLineno, tokenColumn, expectedType, value->descriptor());
    }
    expectedType->put(data, &value);
    next();
  } else {
    parseError(tokenLineno, tokenColumn, "Unexpected token");
  }
}

runtime::Object* TextDecoder::readStructValue(const StructDescriptor* expectedType, int flags) {
  if (expectedType->typeId() != TYPE_KIND_STRUCT) {
    typeError(tokenLineno, tokenColumn, expectedType, "struct");
  }

  runtime::Object* savedInstance = instance;
  instance = NULL;
  runtime::Object* st = readStructFields(expectedType, flags);
  assert(st->isInstanceOf(expectedType));
  instance = savedInstance;
  if (!match(TOKEN_RBRACE)) {
    parseError(tokenLineno, tokenColumn, "Expected '}' after struct");
  }
  return st;
}

void TextDecoder::readListValue(const Type* expectedType, int flags, void* data) {
  assert(expectedType->typeId() == TYPE_KIND_LIST || expectedType->typeId() == TYPE_KIND_SET);
  const Type* elementType = static_cast<const ListType*>(expectedType)->getElementType();
  int elementFlags = 0;
  if (elementType->typeId() == TYPE_KIND_MODIFIED) {
    const ModifiedType* modifiedType = static_cast<const ModifiedType*>(elementType);
    if (modifiedType->isShared()) {
      elementFlags = TM_SHARED;
    }
    elementType = modifiedType->getElementType();
  }
  if (expectedType->typeId() == TYPE_KIND_LIST) {
    for (;;) {
      if (token == TOKEN_END) {
        parseError(tokenLineno, tokenColumn, "Premature end of stream while reading list");
      } else if (token == TOKEN_RBRACKET) {
        break;
      }

      readValue(elementType, elementFlags, expectedType->add(data, NULL));
    }
  } else {
    for (;;) {
      if (token == TOKEN_END) {
        parseError(tokenLineno, tokenColumn, "Premature end of stream while reading list");
      } else if (token == TOKEN_RBRACKET) {
        break;
      }

      // Switching inside the inner loop isn't particularly efficient, but this is a text
      // decoder, let's not over-optimize.
      switch (elementType->typeId()) {
        case TYPE_KIND_BOOL:
        case TYPE_KIND_INTEGER:
        case TYPE_KIND_STRUCT:
        case TYPE_KIND_ENUM: {
          ValueHolder v;
          readValue(elementType, elementFlags, &v);
          expectedType->add(data, &v);
          break;
        }

        case TYPE_KIND_STRING:
        case TYPE_KIND_BYTES: {
          // Read strings in place
          std::vector<std::string>& v = *(std::vector<std::string>*)data;
          v.push_back(std::string());
          readValue(elementType, elementFlags, (void *)&v.back());
          expectedType->add(data, &v);
          break;
        }

        default:
          assert(false && "Invalid set member type");
      }
    }
  }

  if (!match(TOKEN_RBRACKET)) {
    parseError(tokenLineno, tokenColumn, "']' expected after list value");
  }
}

void TextDecoder::readMapValue(const MapType* expectedType, int flags, void* data) {
  if (expectedType->typeId() != TYPE_KIND_MAP) {
    typeError(tokenLineno, tokenColumn, expectedType, "map");
  }
  const Type* keyType = expectedType->getKeyType();
  int keyFlags = 0;
  if (keyType->typeId() == TYPE_KIND_MODIFIED) {
    const ModifiedType* modifiedType = static_cast<const ModifiedType*>(keyType);
    if (modifiedType->isShared()) {
      keyFlags = TM_SHARED;
    }
    keyType = modifiedType->getElementType();
  }
  const Type* valueType = expectedType->getValueType();
  int valueFlags = 0;
  if (valueType->typeId() == TYPE_KIND_MODIFIED) {
    const ModifiedType* modifiedType = static_cast<const ModifiedType*>(valueType);
    if (modifiedType->isShared()) {
      valueFlags = TM_SHARED;
    }
    valueType = modifiedType->getElementType();
  }
  for (;;) {
    if (token == TOKEN_END) {
      parseError(tokenLineno, tokenColumn, "Premature end of stream while reading map value.");
    } else if (token == TOKEN_RBRACE) {
      break;
    }
    void* valueData = NULL;
    switch (keyType->typeId()) {
      case TYPE_KIND_BOOL:
      case TYPE_KIND_INTEGER:
      case TYPE_KIND_STRUCT:
      case TYPE_KIND_ENUM: {
        ValueHolder v;
        readValue(keyType, keyFlags, &v);
        valueData = expectedType->add(data, &v);
        break;
      }

      case TYPE_KIND_STRING:
      case TYPE_KIND_BYTES: {
        // Read strings in place
        std::string v;
        readValue(keyType, keyFlags, &v);
        valueData = expectedType->add(data, &v);
        break;
      }

      default:
        assert(false && "Invalid map key type");
    }
    if (!match(TOKEN_COLON)) {
      parseError(tokenLineno, tokenColumn, "Colon expected after map key");
    }
    if (token == TOKEN_END) {
      parseError(tokenLineno, tokenColumn, "Premature end of stream while reading map");
    }
    readValue(valueType, valueFlags, valueData);
  }
  if (!match(TOKEN_RBRACE)) {
    parseError(tokenLineno, tokenColumn, "'}' expected after map");
  }
}

runtime::Object* TextDecoder::readStructFields(const StructDescriptor* expectedType, int flags) {
  while (token != TOKEN_END) {
    if (token == TOKEN_ID) {
      std::string fieldName = tokenValue;
      next();
      if (!match(TOKEN_COLON)) {
        parseError(tokenLineno, tokenColumn, "Missing colon after field name");
      }
      if (instance == NULL) {
        instance = expectedType->newInstance();
        if (flags & TM_SHARED) {
          addShared(instance);
        }
      }
      const FieldDescriptor* field = expectedType->getField(fieldName);
      if (field == NULL) {
        parseError(tokenLineno, tokenColumn,
            "Unknown field '" + fieldName + "' of type " + expectedType->getFullName());
      }
      const Type* fieldType = field->getType();
      int32_t lineno = tokenLineno;
      int32_t column = tokenColumn;
      int flags = 0;
      if (field->getOptions()->isNullable()) {
        flags |= TM_NULLABLE;
      }

      if (fieldType->typeId() == TYPE_KIND_MODIFIED) {
        const ModifiedType* modifiedType = static_cast<const ModifiedType*>(fieldType);
        if (modifiedType->isShared()) {
          flags |= TM_SHARED;
        }
        fieldType = modifiedType->getElementType();
      }
      readValue(fieldType, flags, fieldAddress(field, instance));
    } else if (token == TOKEN_TYPEREF) {
      uint32_t typeId = std::strtoul(tokenValue.c_str(), NULL, 10);
      next();
      if (!match(TOKEN_LPAREN)) {
        parseError(tokenLineno, tokenColumn, "'(' expected");
      }
      if (token != TOKEN_ID) {
        parseError(tokenLineno, tokenColumn, "type name expected");
      }
      next(); // Skip type name
      if (!match(TOKEN_RPAREN)) {
        parseError(tokenLineno, tokenColumn, "')' expected");
      }
      if (!match(TOKEN_COLON)) {
        parseError(tokenLineno, tokenColumn, "Missing colon after subtype name");
      }
      if (!match(TOKEN_LBRACE)) {
        parseError(tokenLineno, tokenColumn, "'{{' expected");
      }
      // Find root type
      const StructType* base = expectedType;
      while (base->getBaseType() != NULL) {
        base = base->getBaseType();
      }
      const StructDescriptor* subtype = getSubtype(base, typeId);
      if (subtype == NULL) {
        // TODO: Create the instance with the descriptor we know, and
        // Store subtype fields in extension field 0
//        print("No subtype id {0} found for base type {1}", typeId,
//            descriptor->getName());
        //self.pushState(None)
        assert(false && "Implement unknown subtypes");
      }
      readStructFields(subtype, flags);
      if (instance == NULL) {
        instance = subtype->newInstance();
        if (flags & TM_SHARED) {
          addShared(instance);
        }
      }
      if (!instance->isInstanceOf(subtype)) {
        typeError(tokenLineno, tokenColumn, expectedType, subtype);
      }
      assert(instance->isInstanceOf(subtype));
      if (!match(TOKEN_RBRACE)) {
        parseError(tokenLineno, tokenColumn, "'}' expected after subtype");
      }
    } else if (token == TOKEN_RBRACE) {
      break;
    } else {
      parseError(tokenLineno, tokenColumn, "Unexpected token");
    }
  }
  if (instance == NULL) {
    instance = expectedType->newInstance();
    if (flags & TM_SHARED) {
      addShared(instance);
    }
  }
  return instance;
}

void TextDecoder::readch() {
  std::cerr << "[" << ch << "]";
  ch = strm.get();
  ++column;
}

void TextDecoder::newline() {
  lineno += 1;
  column = 1;
  std::cerr << " nl " << lineno << ":" << column << "\n";
}

void TextDecoder::next() {
  // Whitespace loop
  for (;;) {
    if (strm.eof()) {
      newline();
      token = TOKEN_END;
      return;
    } else if (ch == ' ' || ch == '\t') {
      // Horizontal whitespace
      readch();
    } else if (ch == '\n') {
      // Linefeed
      readch();
      newline();
    } else if (ch == '\r') {
      // Carriage return. Look for CRLF pair and count as 1 line.
      readch();
      if (ch == '\n') {
        readch();
      }
      newline();
    } else if (ch == '#') {
      // Comment
      readch();
      while (!strm.eof() && ch != '\n' && ch != '\r') {
        readch();
      }
    } else {
      break;
    }
  }

  tokenValue.clear();
  tokenLineno = lineno;
  tokenColumn = column;
  std::cerr << " tk " << lineno << ":" << column << "\n";

  // Identifier
  if (isNameStartChar(ch)) {
    tokenValue.push_back(ch);
    readch();
    while (!strm.eof() && isNameChar(ch)) {
      tokenValue.push_back(ch);
      readch();
    }

    // Check for keyword
    if (tokenValue == "true") {
      token = TOKEN_TRUE;
    } else if (tokenValue == "false") {
      token = TOKEN_FALSE;
    } else if (tokenValue == "null") {
      token = TOKEN_NULL;
    } else {
      token = TOKEN_ID;
    }
    return;
  }

  // Number
  if (isDigitChar(ch) || ch == '.' || ch == '-') {
    token = TOKEN_INTVAL;
    if (ch == '_') {
      tokenSign = true;
      readch();
    } else {
      tokenSign = false;
    }

    // Hex number check
    if (ch == '0') {
      tokenValue.push_back('0');
      readch();
      if (ch == 'X' || ch == 'x') {
        tokenValue.push_back('x');
        readch();
        while (!strm.eof() && isHexDigitChar(ch)) {
          tokenValue.push_back(ch);
          readch();
        }
        return;
      }
    }

    // Integer part
    while (!strm.eof() && isDigitChar(ch)) {
      tokenValue.push_back(ch);
      readch();
    }

    // Fractional part
    if (ch == '.') {
      readch();

      // Check for case where this isn't a decimal point,
      // but just a dot token.
      if (!isDigitChar(ch) && tokenValue.empty()) {
        readch();
      }

      // It's a float
      token = TOKEN_FLOATVAL;

      tokenValue.push_back('.');
      while (!strm.eof() && isDigitChar(ch)) {
        tokenValue.push_back(ch);
        readch();
      }
    }

    // Exponent part
    if ((ch == 'e' || ch == 'E')) {
      token = TOKEN_FLOATVAL;
      tokenValue.push_back(ch);
      readch();
      if ((ch == '+' || ch == '-')) {
        tokenValue.push_back(ch);
        readch();
      }
      while (!strm.eof() && isDigitChar(ch)) {
        tokenValue.push_back(ch);
        readch();
      }
    }

    if ((ch == 'f' || ch == 'F')) {
      token = TOKEN_FLOATVAL;
      tokenValue.push_back(ch);
      readch();
    }

    return;
  }

  if (ch == '"') {
    readch();
    token = TOKEN_STRING;
    lexString('"');
    return;
  } else if (ch == '\'') {
    readch();
    token = TOKEN_STRING;
    lexString('\'');
    return;
  }

  switch (ch) {
    case ':':
      readch();
      token = TOKEN_COLON;
      return;

    case ',':
      readch();
      token = TOKEN_COMMA;
      return;

    case '.':
      readch();
      token = TOKEN_DOT;
      return;

    case '<':
      readch();
      if (ch == '[') {
        readch();
        token = TOKEN_LBINARY;
      } else {
        parseError(lineno, column, "Expected '[' after '<'");
      }
      return;

    case '[':
      readch();
      token = TOKEN_LBRACKET;
      return;

    case ']':
      readch();
      token = TOKEN_RBRACKET;
      if (ch == '>') {
        readch();
        token = TOKEN_RBINARY;
      }
      return;

    case '{':
      readch();
      token = TOKEN_LBRACE;
      return;

    case '}':
      readch();
      token = TOKEN_RBRACE;
      return;

    case '(':
      readch();
      token = TOKEN_LPAREN;
      return;

    case ')':
      readch();
      token = TOKEN_RPAREN;
      return;

    case '%':
      readch();
      token = TOKEN_OBJREF;
      while (!strm.eof() && isDigitChar(ch)) {
        tokenValue.push_back(ch);
        readch();
      }
      return;

    case '$':
      readch();
      token = TOKEN_TYPEREF;
      while (!strm.eof() && isDigitChar(ch)) {
        tokenValue.push_back(ch);
        readch();
      }
      return;

    default:
      parseError(lineno, column, "Illegal character");
      break;
  }
}

void TextDecoder::lexString(char quoteChar) {
  int charCount = 0;
  for (;;) {
    if (strm.eof()) {
      parseError(lineno, column, "Unterminated string");
    } else if (ch == quoteChar) {
      readch();
      break;
    } else if (ch == '\\') {
      readch();
      switch (ch) {
        case '0':
          tokenValue.push_back('\0');
          readch();
          break;
        case '\\':
          tokenValue.push_back('\\');
          readch();
          break;
        case '\'':
          tokenValue.push_back('\'');
          readch();
          break;
        case '\"':
          tokenValue.push_back('\"');
          readch();
          break;
        case 'r':
          tokenValue.push_back('\r');
          readch();
          break;
        case 'n':
          tokenValue.push_back('\n');
          readch();
          break;
        case 't':
          tokenValue.push_back('\t');
          readch();
          break;
        case 'b':
          tokenValue.push_back('\b');
          readch();
          break;
        case 'v':
          tokenValue.push_back('\v');
          readch();
          break;
        case 'x': {
          // Parse a hexadecimal character in a string.
          char charbuf[3];
          size_t  len = 0;
          readch();
          while (isHexDigitChar(ch) && len < 2) {
            charbuf[len++] = ch;
            readch();
          }

          if (len == 0) {
            parseError(lineno, column, "Malformed escape sequence");
          }

          charbuf[len] = 0;
          long charVal = strtoul(charbuf, NULL, 16);
          tokenValue.push_back(charVal);
          break;
        }

        case 'u':
        case 'U': {
            // Parse a unicode character literal in a string.
            size_t maxLen = (ch == 'u' ? 4 : 8);
            char charbuf[9];
            size_t  len = 0;
            readch();
            while (isHexDigitChar(ch) && len < maxLen) {
              charbuf[len++] = ch;
              readch();
            }
            if (len == 0) {
              parseError(lineno, column, "Malformed escape sequence");
            }

            charbuf[len] = 0;
            uint32_t charVal = strtoul(charbuf, NULL, 16);
            encodeUnicodeChar(charVal);
            break;
          }
        default:
          tokenValue.push_back(ch);
          readch();
          break;
      }
    } else if (ch >= ' ') {
      tokenValue.push_back(ch);
      readch();
    } else {
      parseError(lineno, column, "Malformed escape sequence");
    }

    ++charCount;
  }
}

bool TextDecoder::encodeUnicodeChar(uint32_t charVal) {
  if (charVal < 0x80) {
    tokenValue.push_back(charVal);
  } else if (charVal < 0x800) {
    tokenValue.push_back(0xc0 | (charVal >> 6));
    tokenValue.push_back(0x80 | (charVal & 0x3f));
  } else if (charVal < 0x10000) {
    tokenValue.push_back(0xe0 | (charVal >> 12));
    tokenValue.push_back(0x80 | ((charVal >> 6) & 0x3f));
    tokenValue.push_back(0x80 | (charVal & 0x3f));
  } else if (charVal < 0x100000) {
    tokenValue.push_back(0xf0 | (charVal >> 18));
    tokenValue.push_back(0x80 | ((charVal >> 12) & 0x3f));
    tokenValue.push_back(0x80 | ((charVal >> 6) & 0x3f));
    tokenValue.push_back(0x80 | (charVal & 0x3f));
  } else {
    parseError(lineno, column, "Invalid Unicode character");
  }

  return true;
}

void TextDecoder::typeError(
    int32_t lineno, int32_t column, const descriptors::Type* expected, const std::string& actual) {
  std::string expectedStr;
  describeType(expected, expectedStr);
  parseError(lineno, column, "Type mismatch: cannot assign " + actual + " value to field of type " +
      expectedStr + ".");
}

void TextDecoder::typeError(
    int32_t lineno, int32_t column,
    const descriptors::Type* expected, const descriptors::Type* actual) {
  std::string expectedStr;
  std::string actualStr;
  describeType(expected, expectedStr);
  describeType(actual, actualStr);
  parseError(lineno, column, "Type mismatch: cannot assign " + actualStr +
      " value to field of type " + expectedStr + ".");
}

void TextDecoder::parseError(int32_t lineno, int32_t column, const std::string& msg) {
  std::strstream str;
  str << "ERROR ";
  if (!sourcePath.empty()) {
    str << sourcePath << ':';
  }
  str << lineno << ':' << column << ':' << msg;
  throw ParsingError(str.str());
}

}} // namespace
