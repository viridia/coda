// ============================================================================
// Coda Text Encoder
// ============================================================================

#ifndef CODA_IO_TEXTENCODER_H
#define CODA_IO_TEXTENCODER_H 1

#ifndef CODA_IO_ABSTRACTENCODER_H
  #include "coda/io/abstractencoder.h"
#endif

#include <ostream>

namespace coda {
namespace io {

/**
 * Encoder that serializes into text format.
 */
class TextEncoder : public AbstractEncoder {
public:
  TextEncoder(std::ostream& str)
    : strm(str)
    , indentLevel(0)
    , first(true)
    , state(CLEAR)
    , fieldHeader(false)
    , maxDepth(255)
  {
  }

  Encoder& writeSubtypeHeader(const runtime::StringRef& subtypeName, int32_t subtypeId);
  Encoder& writeFieldHeader(const runtime::StringRef& fieldName, int32_t fieldId);
  Encoder& writeBoolean(bool value);
  Encoder& writeInteger(int32_t value);
  Encoder& writeInteger(int64_t value);
  Encoder& writeFixed16(int16_t value);
  Encoder& writeFixed32(int32_t value);
  Encoder& writeFixed64(int64_t value);
  Encoder& writeFloat(float value);
  Encoder& writeDouble(double value);
  Encoder& writeString(const runtime::StringRef& value);
  Encoder& writeBytes(const runtime::StringRef& value);
  Encoder& writeBeginList(
      coda::descriptors::TypeKind elementKind, size_t length, bool fixed = false);
  Encoder& writeEndList();
  Encoder& writeBeginSet(
      coda::descriptors::TypeKind elementKind, size_t length, bool fixed = false);
  Encoder& writeEndSet();
  Encoder& writeBeginMap(
      coda::descriptors::TypeKind keyKind,
      coda::descriptors::TypeKind valueKind,
      size_t length);
  Encoder& writeEndMap();
  Encoder& writeStruct(const coda::runtime::Object* value, bool shared=true);
  Encoder& writeEndSubtype();

private:
  enum State {
    CLEAR,
    STRUCT,
    CONTAINER,
    MAP_KEY,
    MAP_VALUE
  };

  std::ostream& strm;
  int32_t indentLevel;
  bool first;
  State state;
  bool fieldHeader;
  std::unordered_set<void*> inProgress;
  std::vector<State> states;
  size_t maxDepth;

  void writeBeginStruct();
  void writeEndStruct();
  void indent();
  void beginValue();
};

}} // namespace

#endif // CODA_IO_TEXTENCODER_H
