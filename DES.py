################################################################
#                       DES加解密，                              #
################################################################
import time

hex_bin_box = {
        '0': '0000', '1': '0001', '2': '0010', '3': '0011',
        '4': '0100', '5': '0101', '6': '0110', '7': '0111',
        '8': '1000', '9': '1001', 'a': '1010', 'b': '1011',
        'c': '1100', 'd': '1101', 'e': '1110', 'f': '1111',
}
hex2bin = lambda hexstr: ''.join(hex_bin_box[i] for i in hexstr)             #用于16进制字符串转二进制字符串

# 矩阵转换lambda表达式
translation = lambda item, box: ''.join(item[i - 1] for i in box)

#秘钥的PC1矩阵
K64_56 = [
                57, 49, 41, 33, 25, 17, 9,
                1, 58, 50, 42, 34, 26, 18,
                10, 2, 59, 51, 43, 35, 27,
                19, 11, 3, 60, 52, 44, 36,
                63, 55, 47, 39, 31, 23, 15,
                7, 62, 54, 46, 38, 30, 22,
                14, 6, 61, 53, 45, 37, 29,
                21, 13, 5, 28, 20, 12, 4,
        ]

#秘钥的PC2矩阵
K56_48 = [
        14, 17, 11, 24, 1, 5, 3, 28,
        15, 6, 21, 10, 23, 19, 12, 4,
        26, 8, 16, 7, 27, 20, 13, 2,
        41, 52, 31, 37, 47, 55, 30, 40,
        51, 45, 33, 48, 44, 49, 39, 56,
        34, 53, 46, 42, 50, 36, 29, 32
]

Kleft_shift = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

#获取轮秘钥
def get_Kn(Key):# 生成Ki(共16轮密钥)
        K64 = hex2bin(Key)  #转bit串
        # print(K64[41])
        # print(K64[57])
        # Step1  64bits Key -> 56bits Key：

        K56 = translation(K64, K64_56)
        # print(K56)
        # Step2  circulate left draft

        Cn = [K56[:28]]
        Dn = [K56[28:]]
        for i in range(16):
                # 出错位置，虽然Cn中有17个数，但是我们这里的i是从0开始的，且Kleft_draft[i]对应着Ki+1，
                Cn.append(Cn[-1][Kleft_shift[i]:] + Cn[-1][:Kleft_shift[i]])
        for i in range(16):
                Dn.append(Dn[-1][Kleft_shift[i]:] + Dn[-1][:Kleft_shift[i]])
        # for i in range(17):
        #     print("{:<2}   {}   {}".format(i,Cn[i],Dn[i]))

        # Step3 Ci(56)->Ki(48)
        Kn = [translation(Cn[i] + Dn[i], K56_48) for i in range(1, 17)]
        # for i in range(16):
        #         print('K{:<3}      {}'.format(i+1,Kn[i]))
        return Kn

##处理输入,输入的字符串转ascii(0x)，再分组，每16位0x一组，不足用0补齐
def divide(P):
        l = len(P)
        Pn = []
        while not l % 16 == 0:
                P = P + '0'
                l = len(P)
        else:
                for i in range(0, l, 16):
                        Pn.append(P[i:i + 16])
        return Pn

#E扩展
E_box = [
        32,1,2,3,4,5,
        4,5,6,7,8,9,
        8,9,10,11,12,13,
        12,13,14,15,16,17,
        16,17,18,19,20,21,
        20,21,22,23,24,25,
        24,25,26,27,28,29,
        28,29,30,31,32,1,
]

S_box = [
        [
                0xe, 0x4, 0xd, 0x1, 0x2, 0xf, 0xb, 0x8, 0x3, 0xa, 0x6, 0xc, 0x5, 0x9, 0x0, 0x7,
                0x0, 0xf, 0x7, 0x4, 0xe, 0x2, 0xd, 0x1, 0xa, 0x6, 0xc, 0xb, 0x9, 0x5, 0x3, 0x8,
                0x4, 0x1, 0xe, 0x8, 0xd, 0x6, 0x2, 0xb, 0xf, 0xc, 0x9, 0x7, 0x3, 0xa, 0x5, 0x0,
                0xf, 0xc, 0x8, 0x2, 0x4, 0x9, 0x1, 0x7, 0x5, 0xb, 0x3, 0xe, 0xa, 0x0, 0x6, 0xd,
        ],
        [
                0xf, 0x1, 0x8, 0xe, 0x6, 0xb, 0x3, 0x4, 0x9, 0x7, 0x2, 0xd, 0xc, 0x0, 0x5, 0xa,
                0x3, 0xd, 0x4, 0x7, 0xf, 0x2, 0x8, 0xe, 0xc, 0x0, 0x1, 0xa, 0x6, 0x9, 0xb, 0x5,
                0x0, 0xe, 0x7, 0xb, 0xa, 0x4, 0xd, 0x1, 0x5, 0x8, 0xc, 0x6, 0x9, 0x3, 0x2, 0xf,
                0xd, 0x8, 0xa, 0x1, 0x3, 0xf, 0x4, 0x2, 0xb, 0x6, 0x7, 0xc, 0x0, 0x5, 0xe, 0x9,
        ],
        [
                0xa, 0x0, 0x9, 0xe, 0x6, 0x3, 0xf, 0x5, 0x1, 0xd, 0xc, 0x7, 0xb, 0x4, 0x2, 0x8,
                0xd, 0x7, 0x0, 0x9, 0x3, 0x4, 0x6, 0xa, 0x2, 0x8, 0x5, 0xe, 0xc, 0xb, 0xf, 0x1,
                0xd, 0x6, 0x4, 0x9, 0x8, 0xf, 0x3, 0x0, 0xb, 0x1, 0x2, 0xc, 0x5, 0xa, 0xe, 0x7,
                0x1, 0xa, 0xd, 0x0, 0x6, 0x9, 0x8, 0x7, 0x4, 0xf, 0xe, 0x3, 0xb, 0x5, 0x2, 0xc,
        ],
        [
                0x7, 0xd, 0xe, 0x3, 0x0, 0x6, 0x9, 0xa, 0x1, 0x2, 0x8, 0x5, 0xb, 0xc, 0x4, 0xf,
                0xd, 0x8, 0xb, 0x5, 0x6, 0xf, 0x0, 0x3, 0x4, 0x7, 0x2, 0xc, 0x1, 0xa, 0xe, 0x9,
                0xa, 0x6, 0x9, 0x0, 0xc, 0xb, 0x7, 0xd, 0xf, 0x1, 0x3, 0xe, 0x5, 0x2, 0x8, 0x4,
                0x3, 0xf, 0x0, 0x6, 0xa, 0x1, 0xd, 0x8, 0x9, 0x4, 0x5, 0xb, 0xc, 0x7, 0x2, 0xe,
        ],
        [
                0x2, 0xc, 0x4, 0x1, 0x7, 0xa, 0xb, 0x6, 0x8, 0x5, 0x3, 0xf, 0xd, 0x0, 0xe, 0x9,
                0xe, 0xb, 0x2, 0xc, 0x4, 0x7, 0xd, 0x1, 0x5, 0x0, 0xf, 0xa, 0x3, 0x9, 0x8, 0x6,
                0x4, 0x2, 0x1, 0xb, 0xa, 0xd, 0x7, 0x8, 0xf, 0x9, 0xc, 0x5, 0x6, 0x3, 0x0, 0xe,
                0xb, 0x8, 0xc, 0x7, 0x1, 0xe, 0x2, 0xd, 0x6, 0xf, 0x0, 0x9, 0xa, 0x4, 0x5, 0x3,
        ],
        [
                0xc, 0x1, 0xa, 0xf, 0x9, 0x2, 0x6, 0x8, 0x0, 0xd, 0x3, 0x4, 0xe, 0x7, 0x5, 0xb,
                0xa, 0xf, 0x4, 0x2, 0x7, 0xc, 0x9, 0x5, 0x6, 0x1, 0xd, 0xe, 0x0, 0xb, 0x3, 0x8,
                0x9, 0xe, 0xf, 0x5, 0x2, 0x8, 0xc, 0x3, 0x7, 0x0, 0x4, 0xa, 0x1, 0xd, 0xb, 0x6,
                0x4, 0x3, 0x2, 0xc, 0x9, 0x5, 0xf, 0xa, 0xb, 0xe, 0x1, 0x7, 0x6, 0x0, 0x8, 0xd,
        ],
        [
                0x4, 0xb, 0x2, 0xe, 0xf, 0x0, 0x8, 0xd, 0x3, 0xc, 0x9, 0x7, 0x5, 0xa, 0x6, 0x1,
                0xd, 0x0, 0xb, 0x7, 0x4, 0x9, 0x1, 0xa, 0xe, 0x3, 0x5, 0xc, 0x2, 0xf, 0x8, 0x6,
                0x1, 0x4, 0xb, 0xd, 0xc, 0x3, 0x7, 0xe, 0xa, 0xf, 0x6, 0x8, 0x0, 0x5, 0x9, 0x2,
                0x6, 0xb, 0xd, 0x8, 0x1, 0x4, 0xa, 0x7, 0x9, 0x5, 0x0, 0xf, 0xe, 0x2, 0x3, 0xc,
        ],
        [
                0xd, 0x2, 0x8, 0x4, 0x6, 0xf, 0xb, 0x1, 0xa, 0x9, 0x3, 0xe, 0x5, 0x0, 0xc, 0x7,
                0x1, 0xf, 0xd, 0x8, 0xa, 0x3, 0x7, 0x4, 0xc, 0x5, 0x6, 0xb, 0x0, 0xe, 0x9, 0x2,
                0x7, 0xb, 0x4, 0x1, 0x9, 0xc, 0xe, 0x2, 0x0, 0x6, 0xa, 0xd, 0xf, 0x3, 0x5, 0x8,
                0x2, 0x1, 0xe, 0x7, 0x4, 0xa, 0x8, 0xd, 0xf, 0xc, 0x9, 0x0, 0x3, 0x5, 0x6, 0xb,
        ],
]

# P盒
P_box = [
        16, 7,20,21,29,12,28,17,
        1 ,15,23,26, 5,18,31,10,
        2 ,8 ,24,14,32,27, 3, 9,
        19,13,30, 6,22,11, 4,25,
]

#F函数
def F(R,Ki): #R是32bits，Ki是48bits,
        # print(R)
        R = translation(R, E_box)      #对R进行E拓展
        # print('{:<4}        {}'.format('E',R))
        R = ''.join('0' if R[i]==Ki[i] else '1' for i in range(48))  #对R和Ki进行异或
        # print('{:<4}        {}'.format('Ki^E', R))
        # 确定过S盒的坐标
        ij = [R[i:i+6] for i in range(0,48,6)]     # 按6bit分组
        #print(ij)
        #print(ij[0][1:-1])      #出错位置，取中间四位应该是[1:-1]
        S_box_loca = [int(ij[n][0]+ij[n][-1],2) * 16 + int(ij[n][1:-1],2) for n in range(8)] # 首尾拼接做行，中间四位做列,这里的行列不用减1，因为4行16列，已经包括0的可能性了
        # print(S_box_loca)
        R = ''.join(hex_bin_box[hex((S_box[n][S_box_loca[n]]))[-1]] for n in range(8))
        # print('{:<4}        {}'.format('S', R))
        # 过P盒
        R = translation(R,P_box)
        # print('{:<4}        {}'.format('P', R))
        return R

def festial(l,r,Ki):
        l_n = r
        #print(l_n)
        r_n = F(l_n,Ki)
        r_n = ''.join('0'if l[i] ==r_n[i] else '1' for i in range(32))

        return l_n,r_n

#IP置换
IP = [
        58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4,
        62, 54, 46, 38, 30, 22, 14, 6, 64, 56, 48, 40, 32, 24, 16, 8,
        57, 49, 41, 33, 25, 17, 9, 1, 59, 51, 43, 35, 27, 19, 11, 3,
        61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7
]
#IP逆置换
IP_1=[
        40,8,48,16,56,24,64,32,39,7,47,15,55,23,63,31,
        38,6,46,14,54,22,62,30,37,5,45,13,53,21,61,29,
        36,4,44,12,52,20,60,28,35,3,43,11,51,19,59,27,
        34,2,42,10,50,18,58,26,33,1,41, 9,49,17,57,25
]

def Enc_Dec(P,Key,choice):
        Pn = divide(P)
        result=''
        Kn = get_Kn(Key)
        if choice=='2':
                Kn.reverse()
        for p in Pn:
                p = ''.join(hex_bin_box[i] for i in P)      #转为二进制
                #print(p)
                p = translation(p, IP)                  #IP置换
                # print(p)
                l = p[0:32]
                r = p[32:]
                for i in range(16):
                        # print("{:<10}Round{}".format(' ',i + 1))
                        # print('{:<4}        {}'.format('Ki', Kn[i]))
                        l,r = festial(l,r,Kn[i])
                        # print('{:<4}        {}'.format('r', r))
                        # print('{:<4}        {}\n'.format('l', l))

                l,r = r,l
                result = result + l+r
        result = translation(result,IP_1)               #IP_1 置换
        return result

if __name__ == '__main__':
        # for i in range(16):
        #         print("case {}:\n\t return \"{}\";".format(i,hex_bin[hex(i)[-1]]))
        choice = input("Encrypt to 1,Decrypt to 2:")
        if choice == '1':
                #P = str(input("请输入要加密的字符串：").encode('ascii').hex())  # 明文P
                #P = input("请输入要加密的16进制串：")
                #Key = input("请输入秘钥：")  # 密钥Key（64bits）
                P = '02468aceeca86420'
                Key = '0f1571c947d9e859'
                #P = 'a406753854abcdef'
                #Key = 'a34457799bbcdff1'i
                while not len(Key) == 16:
                        Key = input("请输入秘钥：")  # 密钥Key（64bits）
                start = time.time()
                for i in range(10):
                        M = Enc_Dec(P,Key,choice)
                print("10 times average it costs {}s ".format((time.time()-start)/10))
                #print(M)
                s = ''.join(hex(int(M[i:i+4],2))[-1]for i in range(0,64,4))
                print("{} 经过秘钥 {} 加密得到：{}".format(P,Key,s))

        elif choice == '2':
                #M = input("请输入要解密的16进制串：")  # 密文M
                # Key = input("请输入秘钥：")  # 密钥Key（64bits）
                M = 'da02ce3a89ecac3b'
                Key = '0f1571c947d9e859'
                while not len(Key) == 16:
                        Key = input("请输入秘钥：")  # 密钥Key（64bits）
                P = Enc_Dec(M,Key,choice)
                s = ''.join(hex(int(P[i:i + 4], 2))[-1] for i in range(0, 64, 4))
                print("解密得到：", s)







