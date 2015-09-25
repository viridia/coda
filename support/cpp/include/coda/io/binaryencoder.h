// ============================================================================
// Coda Binary Encoder
// ============================================================================

#ifndef CODA_IO_BINARYENCODER_H
#define CODA_IO_BINARYENCODER_H 1

#ifndef CODA_IO_ABSTRACTENCODER_H
  #include "coda/io/abstractencoder.h"
#endif

#ifndef CODA_IO_BINARYFORMAT_H
  #include "coda/io/binaryformat.h"
#endif

#include <ostream>

namespace coda {
namespace io {

/**
 * Encoder that serializes into binary format.
 */
class BinaryEncoder : public AbstractEncoder {
public:
  BinaryEncoder(std::ostream& str);

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
  Encoder& writeStruct(const coda::runtime::Object* value, bool shared=false);
  Encoder& writeEndSubtype();

private:
  enum State {
    CLEAR,
    STRUCT,
    CONTAINER,
    MAP_KEY,
    MAP_VALUE,
    SUBTYPE
  };

  std::ostream& strm;
  State state;
  std::unordered_set<void*> inProgress;
  std::vector<State> states;
  int32_t subtypeId;
  int32_t fieldId;
  int32_t lastFieldId;

  void beginValue(DataType dt);
  void beginSubtype();
  void writeUByte(uint8_t);
  void writeVarInt(uint32_t);
  void writeVarInt(uint64_t);
  static uint32_t zigZagEncode(int32_t value);
  static uint64_t zigZagEncode(int64_t value);
};

}} // namespace

#endif // CODA_IO_TEXTENCODER_H
