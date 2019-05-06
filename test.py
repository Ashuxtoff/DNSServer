import binascii

s = 'abcd'
bs = s.encode()
hs = binascii.unhexlify(s)
print(bs)
print(hs)

a = 'abcdefg'
print(a[1:4])
print(list('aabf
'))