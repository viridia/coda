/* ================================================================== *
 * Address classes unit test
 * ================================================================== */

#include "gtest/gtest.h"
#include "coda/descriptors.h"
#include "coda/io/textencoder.h"
#include "coda/io/textdecoder.h"
#include "coda/runtime/typeregistry.h"
#include "coda/types.h"

#include <sstream>
#include <iostream>

namespace coda {
using namespace coda::descriptors;

TEST(TextCodecTest, TestEncodeDecode) {
  std::stringstream strm;
  coda::io::TextEncoder encoder(strm);
  descriptors::StructType::DESCRIPTOR.write(&encoder);
  coda::io::TextEncoder encoder2(std::cerr);
  descriptors::StructType::DESCRIPTOR.write(&encoder2);
  std::string sourcePath("test");
  coda::io::TextDecoder decoder(strm, &runtime::TypeRegistry::getInstance(), sourcePath);
  descriptors::StructType* st = decoder.read<descriptors::StructType>();
  EXPECT_TRUE(isa<descriptors::StructType>(st));
//  self.assertEqual(st.getFullName(), descriptors.StructType.DESCRIPTOR.getFullName())
}

}
