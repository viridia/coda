/* ================================================================== *
 * Unit test main module.
 * ================================================================== */

#include "gtest/gtest.h"

char* test_data_dir = NULL;

int main(int argc, char **argv) {
  // Initialize and run tests.
  testing::InitGoogleTest(&argc, argv);
  assert(argc == 2);
  test_data_dir = argv[1];
  return RUN_ALL_TESTS();
}
