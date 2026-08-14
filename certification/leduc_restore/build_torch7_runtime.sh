#!/bin/bash
# Golden-Leduc-engine restoration, step 1: authentic Torch7 runtime.
# Reproduces the DS_D2_TORCH7_THREEWAY.md documented build (LuaJIT 2.1 +
# paths + cwrap + torch7 @ 814ea4a, -O2 -ffp-contract=off) in an isolated
# prefix. Environment delta vs D2 (recorded, unavoidable): the DS-bundled
# OpenBLAS cd143947… died with the workspace; this build uses the
# system/current BLAS resolved by torch7's cmake — the restored engine is
# therefore certified against FRESH oracles from this runtime (new
# baseline), not against the lost lua_trace corpus.
set -e
PREFIX=/workspace/torch_runtime
NICE="nice -n 15"
mkdir -p "$PREFIX"
export CFLAGS="-O2 -ffp-contract=off"
export CXXFLAGS="-O2 -ffp-contract=off"

echo "== LuaJIT 2.1 =="
cd /workspace/luajit
$NICE make -j2 PREFIX="$PREFIX" CCOPT="-O2 -ffp-contract=off -fomit-frame-pointer" >/tmp/build_luajit.log 2>&1
make install PREFIX="$PREFIX" >>/tmp/build_luajit.log 2>&1
ln -sf "$PREFIX"/bin/luajit-2.1* "$PREFIX/bin/luajit" 2>/dev/null || true
"$PREFIX/bin/luajit" -v

CMVARS=(-DCMAKE_INSTALL_PREFIX="$PREFIX" -DCMAKE_BUILD_TYPE=Release
  -DCMAKE_C_FLAGS="-O2 -ffp-contract=off"
  -DCMAKE_CXX_FLAGS="-O2 -ffp-contract=off"
  -DLUA_INCDIR="$PREFIX/include/luajit-2.1" -DLUA_LIBDIR="$PREFIX/lib"
  -DLUADIR="$PREFIX/share/lua/5.1" -DLIBDIR="$PREFIX/lib/lua/5.1"
  -DLUALIB=luajit-5.1 -DLUA="$PREFIX/bin/luajit" -DWITH_LUAJIT21=ON)

echo "== paths =="
cd /workspace/torch/paths
mkdir -p build && cd build
$NICE cmake .. "${CMVARS[@]}" >/tmp/build_paths.log 2>&1
$NICE make -j2 install >>/tmp/build_paths.log 2>&1

echo "== cwrap =="
cd /workspace/torch/cwrap
mkdir -p build && cd build
$NICE cmake .. "${CMVARS[@]}" >/tmp/build_cwrap.log 2>&1
$NICE make -j2 install >>/tmp/build_cwrap.log 2>&1

echo "== torch7 @ 814ea4a =="
cd /workspace/torch/torch7
mkdir -p build && cd build
$NICE cmake .. "${CMVARS[@]}" >/tmp/build_torch7.log 2>&1
$NICE make -j2 install >>/tmp/build_torch7.log 2>&1

echo "== validation =="
export LUA_PATH="$PREFIX/share/lua/5.1/?.lua;$PREFIX/share/lua/5.1/?/init.lua;;"
export LUA_CPATH="$PREFIX/lib/lua/5.1/?.so;;"
"$PREFIX/bin/luajit" -e '
require "torch"
torch.manualSeed(42)
local g = torch.Generator and "" or ""
io.write("torch loaded; first u32 after manualSeed(42): ")
print(torch.random(0, 4294967295))
print("tensor smoke:", torch.Tensor{1,2,3}:sum())
'
echo "TORCH7 RUNTIME BUILD COMPLETE"
