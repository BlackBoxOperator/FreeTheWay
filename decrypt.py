#!/usr/bin/env python
# -*- coding: utf-8 -*-

def decrypt_token(fn):
    global phrase
    get = pexpect.spawn(f'openssl rsautl -inkey meta/key.txt -decrypt -in {fn}')
    get.expect("Enter pass phrase for meta/key.txt:")
    if not phrase: phrase = getpass('Enter pass phrase for meta/key.txt:')
    get.sendline(phrase)
    get.expect(pexpect.EOF)
    return get.before.decode('utf-8').strip()

phrase = None
