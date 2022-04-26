byte_size = 8
int_byte_size = 4 * byte_size  # 32位系统
char_byte_size = 1 * byte_size


def bits_2_bytes(bits):
    if len(bits) % byte_size != 0:
        print("error")
        exit(1)
    res = []
    for i in range(0, len(bits), byte_size):
        res.append(bits[i:i + byte_size])
    return res


def str_2_bits(s):
    res = []
    for c in s:
        res.extend(char_2_bits(c))
    return res


def char_2_bits(c):
    bin_str = bin(ord(c))[2:]
    bin_str = bin_str.zfill(char_byte_size)
    return [int(i) for i in bin_str]


def int_2_bits(a):
    if a > 2 ** (int_byte_size - 1) \
            or a < -2 ** (int_byte_size - 1):
        print("error")
        exit(1)
    if a >= 0:
        bin_str = bin(a)[2:]
        bin_str = bin_str.zfill(int_byte_size)
        return [int(i) for i in bin_str]
    else:
        a = -a
        bin_str = bin(a)[2:]
        bin_str = bin_str.zfill(int_byte_size)
        for i in range(int_byte_size):
            if bin_str[i] == '0':
                bin_str = bin_str[:i] + '1' + bin_str[i + 1:]
            else:
                bin_str = bin_str[:i] + '0' + bin_str[i + 1:]
        bin_str = "1" + bin_str[1:]
        bin_str = bin(int(bin_str, 2) + 1)[2:]
        return [int(i) for i in bin_str]
