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
    volatile float fNan = __builtin_nanf("");
    if (__builtin_fpclassify(11, 12, 13, 14, 15, fNan) != 11) {
        return 1;
    }
    volatile float fInf = __builtin_inff();
    if (__builtin_fpclassify(11, 12, 13, 14, 15, fInf) != 12) {
        return 1;
    }
    volatile float fOne = 1.f;
    if (__builtin_fpclassify(11, 12, 13, 14, 15, fOne) != 13) {
        return 1;
    }
    volatile float fZero = 0.f;
    if (__builtin_fpclassify(11, 12, 13, 14, 15, fZero) != 15) {
        return 1;
    }
    volatile double dNan = __builtin_nan("");
    if (__builtin_fpclassify(11, 12, 13, 14, 15, dNan) != 11) {
        return 1;
    }
    volatile double dInf = __builtin_inf();
    if (__builtin_fpclassify(11, 12, 13, 14, 15, dInf) != 12) {
        return 1;
    }
    volatile double dOne = 1.;
    if (__builtin_fpclassify(11, 12, 13, 14, 15, dOne) != 13) {
        return 1;
    }
    volatile double dZero = 0.;
    if (__builtin_fpclassify(11, 12, 13, 14, 15, dZero) != 15) {
        return 1;
    }
#ifdef __clang__ // TODO: dragonegg uses native calls which do not work with X86_FP80
    volatile long double lNan = __builtin_nanl("");
    if (__builtin_fpclassify(11, 12, 13, 14, 15, lNan) != 11) {
        return 1;
    }
    volatile long double lInf = __builtin_infl();
    if (__builtin_fpclassify(11, 12, 13, 14, 15, lInf) != 12) {
        return 1;
    }
    volatile long double lOne = 1.;
    if (__builtin_fpclassify(11, 12, 13, 14, 15, lOne) != 13) {
        return 1;
    }
    volatile long double lZero = 0.;
    if (__builtin_fpclassify(11, 12, 13, 14, 15, lZero) != 15) {
        return 1;
    }
#endif
    return 0;
}
