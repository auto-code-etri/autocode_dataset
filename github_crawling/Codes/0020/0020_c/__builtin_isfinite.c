/*
 * Copyright (c) 2017, 2020, Oracle and/or its affiliates.
 *
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification, are
 * permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this list of
 * conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice, this list of
 * conditions and the following disclaimer in the documentation and/or other materials provided
 * with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its contributors may be used to
 * endorse or promote products derived from this software without specific prior written
 * permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
 * OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */
int main() {
    volatile float a = __builtin_nanf("");
    if (__builtin_isfinite(a)) {
        return 1;
    }
    volatile float b = __builtin_inff();
    if (__builtin_isfinite(b)) {
        return 1;
    }
    volatile double c = __builtin_nan("");
    if (__builtin_isfinite(c)) {
        return 1;
    }
    volatile double d = __builtin_inf();
    if (__builtin_isfinite(d)) {
        return 1;
    }
#ifdef __clang__ // TODO: dragonegg uses native calls which do not work with X86_FP80
    volatile long double e = __builtin_nanl("");
    if (__builtin_isfinite(e)) {
        return 1;
    }
    volatile long double f = __builtin_infl();
    if (__builtin_isfinite(f)) {
        return 1;
    }
#endif
    volatile float g = 0;
    if (!__builtin_isfinite(g)) {
        return 1;
    }
    volatile double h = 0;
    if (!__builtin_isfinite(h)) {
        return 1;
    }
#ifdef __clang__ // TODO: dragonegg uses native calls which do not work with X86_FP80
    volatile long double i = 0;
    if (!__builtin_isfinite(i)) {
        return 1;
    }
#endif
    return 0;
}
