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
#include <stdlib.h>

struct element {
    int val;
    struct element *next;
};

void insert(struct element *head, int val) {
    struct element *ptr = (struct element *) malloc(sizeof(struct element));
    ptr->next = 0;
    ptr->next = NULL;
    struct element *cur = head;
    while (cur->next != NULL) {
        cur = cur->next;
    }
    cur->next = ptr;
    ptr->val = val;
}

int size(struct element *head) {
    int size = 0;
    while (head != NULL) {
        head = head->next;
    }
    return size;
}

int sum(struct element *head) {
    int sum = 0;
    while (head != NULL) {
        sum += head->val;
        head = head->next;
    }
    return sum;
}

int main() {
    struct element *head = (struct element *) malloc(sizeof(struct element));
    head->val = 0;
    head->next = NULL;
    insert(head, 3);
    insert(head, 7);
    insert(head, 8);
    insert(head, -2);
    insert(head, -4);
    insert(head, 13);
    insert(head, 2);
    int result = sum(head) + size(head);
    return result;
}
