// ============================================================================
// Coda Binary Format
// ============================================================================

#ifndef CODA_IO_BINARYFORMAT_H
#define CODA_IO_BINARYFORMAT_H 1

namespace coda {
namespace io {

/** Defines the byte codes that introduce a field in the binary stream. */
enum DataType {
  DT_END = 0,       // End of a struct
  DT_ZERO = 1,      // Constant integer 0
  DT_ONE = 2,       // Constant integer 1
  DT_VARINT = 3,    // Variable-length integer
  DT_FIXED16 = 4,   // 16-bit fixed-width integer
  DT_FIXED32 = 5,   // 32-bit fixed-width integer
  DT_FIXED64 = 6,   // 64-bit fixed-width integer
  DT_FLOAT = 7,     // 32-bit float
  DT_DOUBLE = 8,    // 64-bit float
  DT_BYTES = 9,     // String or Bytes type (followed by length)
  DT_LIST = 10,     // List of items (followed by length)
  DT_PLIST = 11,    // List of fixed-width items (followed by format and length)
  DT_MAP = 12,      // Map of items (followed by length)
  DT_STRUCT = 13,   // Beginning of a struct
  DT_SSTRUCT = 14,  // Beginning of a shared struct
  DT_SUBTYPE = 15,  // Beginning of subtype data, field ID is actually subtype ID

  // Extended types - low bits must be 0
  DT_SHARED_REF = 0x10,   // Reference to a shared object (followed by object id). Used in maps/lists.
  DT_SHARED_DEF = 0x20,   // Definition of a shared object (followed by struct). Used in maps/lists.

  DT_MAXVAL = DT_SUBTYPE
};

}} // namespace

#endif // CODA_IO_TEXTENCODER_H
