#!/bin/bash

cd crypto-cpp
mkdir -p build/Release

CMAKE_CXX_COMPILER="g++"
if [ "$(uname)" == "Darwin" ]; then
    IFS='-' read -r -a TARGET_ARR_WRONG_ORDER <<< "$PLAT"
    TARGET="${TARGET_ARR_WRONG_ORDER[2]}-apple-macos${TARGET_ARR_WRONG_ORDER[1]}"
    echo "Targeting ${TARGET}"

    sed -i'.original' "s/\${CMAKE_CXX_FLAGS} -std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC/-std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC \${CMAKE_CXX_FLAGS} -target ${TARGET}/" CMakeLists.txt
    CMAKE_CXX_COMPILER="clang++"
  else
    sed -i'.original' "s/\${CMAKE_CXX_FLAGS} -std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC/-std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC \${CMAKE_CXX_FLAGS}/" CMakeLists.txt
fi

cat CMakeLists.txt
(cd build/Release; cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER="${CMAKE_CXX_COMPILER}" -DCMAKE_CXX_FLAGS="-Wno-type-limits -Wno-range-loop-analysis -Wno-unused-parameter" ../..)
make -C build/Release
if [ $? -ne 0 ]; then
  exit 1
fi
cp build/Release/src/starkware/crypto/ffi/libcrypto_c_exports.* ../starknet_py/utils/crypto
