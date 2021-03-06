// ============================================================================
// Coda Text Encoder
// ============================================================================

#ifndef CODA_IO_TEXTDECODER_H
#define CODA_IO_TEXTDECODER_H 1

#ifndef CODA_IO_ABSTRACTDECODER_H
  #include "coda/io/abstractdecoder.h"
#endif

#include <istream>

namespace coda {
namespace runtime {
class Object;
}
namespace types {
class GenericList;
class GenericSet;
class GenericMap;
}
namespace io {

/**
 * Exception thrown by encoders and decoders.
 */
class ParsingError : public EncodingError {
public:
  ParsingError(const std::string& msg) : EncodingError(msg) {}
};

/**
 * Decoder that deserializes from text format.
 */
class TextDecoder : public AbstractDecoder {
public:
  TextDecoder(std::istream& strm, runtime::TypeRegistry* typeRegistry, const std::string& srcPath)
    : AbstractDecoder(typeRegistry)
    , strm(strm)
    , instance(NULL)
    , lineno(1)
    , column(1)
    , sourcePath(srcPath)
    , token(TOKEN_UNSET)
    , tokenLineno(1)
    , tokenColumn(1)
  {
  }

  runtime::Object* readObject(const coda::descriptors::StructDescriptor* descriptor);

private:
  enum Token {
    TOKEN_END = 0,
    TOKEN_UNSET,
    TOKEN_COLON,
    TOKEN_COMMA,
    TOKEN_DOT,
    TOKEN_LBINARY,
    TOKEN_RBINARY,
    TOKEN_LBRACKET,
    TOKEN_RBRACKET,
    TOKEN_LBRACE,
    TOKEN_RBRACE,
    TOKEN_LPAREN,
    TOKEN_RPAREN,
    TOKEN_FLOATVAL,
    TOKEN_INTVAL,
    TOKEN_STRING,
    TOKEN_ID,
    TOKEN_OBJREF,
    TOKEN_TYPEREF,
    TOKEN_TRUE,
    TOKEN_FALSE,
    TOKEN_NULL,
  };

  /** Flags used when deserializing object references. */
  enum TypeMod {
    TM_CONST = (1<<0),
    TM_SHARED = (1<<1),
    TM_NULLABLE = (1<<2),
  };

  runtime::Object* readStructFields(const descriptors::StructDescriptor* expectedType, int flags);
  runtime::Object* readStructValue(const descriptors::StructDescriptor* expectedType, int flags);
  void readValue(const descriptors::Type* expectedType, int flags, void* data);
  void readBytesValue(std::string& data);
  void readListValue(const types::GenericList* expectedType, int flags, void* data);
  void readSetValue(const types::GenericSet* expectedType, int flags, void* data);
  void readMapValue(const types::GenericMap* expectedType, int flags, void* data);

  template<class KeyType, class ValueType>
  void readMapElements(
      const types::GenericMap* mapType,
      const descriptors::Type* keyType,
      int keyTypeFlags,
      const descriptors::Type* valueType,
      int valueTypeFlags,
      void* data);

  template<class T>
  void readListElements(
      const descriptors::Type* elementType,
      int elementFlags,
      std::vector<T>& data);

  template<class T>
  void readSetElements(
      const descriptors::Type* elementType,
      int elementFlags,
      std::unordered_set<T>& data);

  /** Match a token. */
  bool match(Token tok) {
    if (token == tok) {
      next();
      return true;
    }
    return false;
  }

  /** Read the next token from the input stream. */
  void next();
  void newline();
  void lexString(char quoteChar);
  void typeError(int32_t lineno, int32_t column,
      const descriptors::Type* expected, const std::string& actual);
  void typeError(int32_t lineno, int32_t column,
      const descriptors::Type* expected, const descriptors::Type* actual);
  void parseError(int32_t lineno, int32_t column, const std::string& msg);
  bool encodeUnicodeChar(uint32_t charVal);
  void readch();

  /** A struct that's large enough to contain any primitive value. */
  union ValueHolder {
    int16_t i16;
    int32_t i32;
    int64_t i64;
    float f32;
    double f64;
    void *vp;
  };

  std::istream& strm;
  runtime::Object* instance;
  int32_t lineno;
  int32_t column;
  const std::string& sourcePath;

  int ch;
  Token token;
  std::string tokenValue;
  bool tokenSign;
  int32_t tokenLineno;
  int32_t tokenColumn;
};

}} // namespace

#endif // CODA_IO_TEXTENCODER_H
