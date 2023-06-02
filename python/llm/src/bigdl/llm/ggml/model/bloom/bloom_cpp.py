#
# Copyright 2016 The BigDL Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ===========================================================================
#
# This file is adapted from
# https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/llama_cpp.py
#
# MIT License
#
# Copyright (c) 2023 Andrei Betlen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This would makes sure Python is aware there is more than one sub-package within bigdl,
# physically located elsewhere.
# Otherwise there would be module not found error in non-pip's setting as Python would
# only search the first bigdl package and end up finding only one sub-package.

import sys
import os
import ctypes
from ctypes import (
    c_int,
    c_float,
    c_char_p,
    c_void_p,
    c_bool,
    POINTER,
    Structure,
    Array,
    c_uint8,
    c_size_t,
)
import pathlib


# Load the library
def _load_shared_library(lib_base_name: str):
    # Determine the file extension based on the platform
    if sys.platform.startswith("linux"):
        lib_ext = ".so"
    elif sys.platform == "darwin":
        lib_ext = ".so"
    elif sys.platform == "win32":
        lib_ext = ".dll"
    else:
        raise RuntimeError("Unsupported platform")

    # Construct the paths to the possible shared library names (python/llm/src/bigdl/llm/libs)
    _base_path = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
    _base_path = _base_path / 'libs'
    # Searching for the library in the current directory under the name "libbloom" (default name
    # for bloomcpp) and "bloom" (default name for this repo)
    _lib_paths = [
        _base_path / f"lib{lib_base_name}{lib_ext}",
        _base_path / f"{lib_base_name}{lib_ext}",
    ]

    if "BLOOM_CPP_LIB" in os.environ:
        lib_base_name = os.environ["BLOOM_CPP_LIB"]
        _lib = pathlib.Path(lib_base_name)
        _base_path = _lib.parent.resolve()
        _lib_paths = [_lib.resolve()]

    # Add the library directory to the DLL search path on Windows (if needed)
    if sys.platform == "win32" and sys.version_info >= (3, 8):
        os.add_dll_directory(str(_base_path))

    # Try to load the shared library, handling potential errors
    for _lib_path in _lib_paths:
        if _lib_path.exists():
            try:
                return ctypes.CDLL(str(_lib_path))
            except Exception as e:
                raise RuntimeError(f"Failed to load shared library '{_lib_path}': {e}")

    raise FileNotFoundError(f"Shared library with base name '{lib_base_name}' not found")


# Specify the base name of the shared library to load
_lib_base_name = "bloom"

# Load the library
_lib = _load_shared_library(_lib_base_name)


def bloom_load(fname: bytes, n_ctx: c_int, n_threads: c_int) -> c_void_p:
    return _lib.bloom_load(fname, n_ctx, n_threads)


_lib.bloom_load.argtypes = [c_char_p, c_int, c_int]
_lib.bloom_load.restype = c_void_p


def bloom_free(ctx: c_void_p):
    return _lib.bloom_free(ctx)


_lib.bloom_free.argtypes = [c_void_p]
_lib.bloom_free.restype = None


def bloom_run(ctx: c_void_p,
              seed: c_int,
              n_threads: c_int,
              n_batch: c_int,
              n_predict: c_int,
              match_str: c_bool,
              prompt: bytes,
              buf: bytes) -> c_int:
    return _lib.bloom_run(ctx, seed, n_threads, n_batch, n_predict, match_str, prompt, buf)


_lib.bloom_run.argtypes = [c_void_p, c_int, c_int, c_int, c_int, c_bool, c_char_p, c_char_p]
_lib.bloom_run.restype = c_int

# ------------------------------------------------------------------- #