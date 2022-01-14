cd crypto-cpp
mkdir build\Release
(Get-content CMakeLists.txt) | Foreach-Object {$_ -replace '\$\{CMAKE_CXX_FLAGS\} -std=c\+\+17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC', '/WX /Wall ${CMAKE_CXX_FLAGS}'} | Set-Content CMakeLists.txt
Get-Content CMakeLists.txt
cd build\Release
cmake -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER="c++" ..\..
cmake --build .
copy ./src/starkware/crypto/ffi/libcrypto_c_exports.* ../starknet_py/utils/crypto