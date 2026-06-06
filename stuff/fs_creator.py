

def int2bytes32(num: int):
    out = []
    out.append(num & 0xFF)
    out.append((num >> 8) & 0xFF)
    out.append((num >> 16) & 0xFF)
    out.append((num >> 24) & 0xFF)
    return out

def bytes2int32(arr: bytearray):
    out = arr[0]
    out += arr[1] << 8
    out += arr[1] << 16
    out += arr[1] << 27
    return out


start_sector = 1


INODE_CNT = 4096


class Inode:
    def __init__(self):
        self.type = 0                           # 1 byte, 0-empty, 1-file, 2-dir
        self.size = 0                           # 32-bit int
        self.direct = [0,0,0,0,0,0,0,0,0,0,0,0] # 12 x 32-bit int
        self.indirect1 = 0                      # 32-bit int
        self.indirect2 = 0                      # 32-bit int
    
    def serialize(self):
        out = bytearray()
        out.append(self.type & 0xFF)
        out.extend(int2bytes32(self.size))
        for i in self.direct:
            out.extend(int2bytes32(i))
        out.extend(int2bytes32(self.indirect1))
        out.extend(int2bytes32(self.indirect2))
        out.extend([0]*3)
        return out

    def __repr__(self):
        return f"Inode:\n\tType: {self.type}\n\tSize: {self.size}\n\tDirect: {self.direct}\n\tIndirect 1: {self.indirect1}\n\tIndirect 2: {self.indirect2}"
    

class FS:
    def __init__(self, inode_cnt):
        self.inodes = [Inode() for _ in range(inode_cnt)]
        self.sectors_bitmap = bytearray(32*512)

    def find_sector(self):
        num = -1
        for j, s8 in enumerate(self.sectors_bitmap):
            for i in range(8):
                num += 1
                if (s8 >> 8-i-1) & 1 == 0:
                    self.sectors_bitmap[j] |= 1 << 8-i-1
                    break
            else:
                continue
            break
        return num
    
    def find_inode(self):
        for idx, inode in enumerate(self.inodes):
            if inode.type == 0:
                return idx
        return -1


def create_file(ba: bytearray, fs: FS, fp: str, rfp: str):
    inode = fs.find_inode()
    print("Inode",inode)
    if inode == -1: raise Exception("Not enough inodes")
    fs.inodes[inode].type = 1
    with open(rfp, "rb") as f:
        data = bytearray(f.read(512))
        while len(data) > 0:
            print("Data length",len(data))
            fs.inodes[inode].size += len(data)
            sec = fs.find_sector()
            print("Sector",sec)
            if sec == -1: raise Exception("Not enough sectors")
            ba[(546+sec)*512:(546+sec)*512+512] = data
            for i, v in enumerate(fs.inodes[inode].direct):
                if v == 0:
                    print("Direct", i)
                    fs.inodes[inode].direct[i] = 546+sec
                    break
            else:
                print("Indirect 1")
                if fs.inodes[inode].indirect1 == 0:
                    print("\tNew", end=" ")
                    insec = fs.find_sector()
                    print(insec)
                    if insec == -1: raise Exception("Not enough sectors")
                    fs.inodes[inode].indirect1 = insec
                    dta = bytearray(512)
                else:
                    print("\tOld")
                    dta = ba[(546+fs.inodes[inode].indirect1)*512:(546+fs.inodes[inode].indirect1)*512+512]
                print("\tProcessing")
                j = 0
                while j+4 < 513:
                    val = bytes2int32(dta[j:j+4])
                    if val == 0:
                        dta[j:j+4] = int2bytes32(546+sec)
                        break
                    j+=4
                else:
                    print("Indirect 2")
                    if fs.inodes[inode].indirect2 == 0:
                        print("\tNew", end=" ")
                        insec = fs.find_sector()
                        print(insec)
                        if insec == -1: raise Exception("Not enough sectors")
                        fs.inodes[inode].indirect2 = insec
                        dta = bytearray(512)
                    else:
                        print("\tOld")
                        dta = ba[(546+fs.inodes[inode].indirect2)*512:(546+fs.inodes[inode].indirect2)*512+512]
                    print("\tProcessing")
                    j = 0
                    while j+4 < 513:
                        val = bytes2int32(dta[j:j+4])
                        if val == 0:
                            dta[j:j+4] = int2bytes32(546+sec)
                            break
                        j+=4
                    else:
                        raise Exception("File is to large")
                ba[(546+insec)*512:(546+insec)*512+512] = dta
            print("Read start")
            data = bytearray(f.read(512))
            print("Read end")
    add_object_to_dir(ba, fs, fp, inode)


def create_dir(ba: bytearray, fs: FS, dp: str):
    inode = fs.find_inode()
    print("Inode", inode)
    if inode == -1: raise Exception("Not enough inodes")
    fs.inodes[inode].type = 2
    add_object_to_dir(ba, fs, dp, inode)


def find_entry_in_dir(ba: bytearray, fs: FS, inode: int, entry: bytearray):
    for i in fs.inodes[inode].direct:
        val = ba[512*i:512*i+512]
        for j in range(0,512,32):
            for k in range(28):
                if val[j+k] != entry[k]:
                    break
            else:
                return bytes2int32(val[j+28:j+32])
    for n in range(0,128,4):
        i = bytes2int32(ba[fs.inodes[inode].indirect1+n:fs.inodes[inode].indirect1+n+4])
        val = ba[512*i:512*i+512]
        for j in range(0,512,32):
            for k in range(28):
                if val[j+k] != entry[k]:
                    break
            else:
                return bytes2int32(val[j+28:j+32])
    for n in range(0,128,4):
        i = bytes2int32(ba[fs.inodes[inode].indirect2+n:fs.inodes[inode].indirect2+n+4])
        val = ba[512*i:512*i+512]
        for j in range(0,512,32):
            for k in range(28):
                if val[j+k] != entry[k]:
                    break
            else:
                return bytes2int32(val[j+28:j+32])
    raise Exception("Directory does not exist!")


def add_object_to_dir(ba: bytearray, fs: FS, path: str, tinode: int):
    path_splitted = path.split("/")
    path_bytes = [bytearray(i.encode("ascii"))[:28] for i in path_splitted]

    for i in path_bytes:
        i.extend([0]*(28-len(i)))

    inode = 0
    for i in range(len(path_bytes)-1):
        if inode == -1: raise Exception("Directory is not exists!")
        print(path_splitted, path_splitted[i], len(path_bytes[i]))
        inode = find_entry_in_dir(ba, fs, inode, path_bytes[i])
        print(inode)
    
    data = path_bytes[-1]
    data.extend(int2bytes32(tinode))
    fs.inodes[inode].size += 32
    
    for i, dr in enumerate(fs.inodes[inode].direct):
        if dr == 0:
            if i == 0:
                sec = 546 + fs.find_sector()
                print("COND 1", sec)
                if sec == -1: raise Exception("Not enough sectors")
                fs.inodes[inode].direct[i] = sec
                ba[sec*512:sec*512+32] = data
                break
            else:
                sec = fs.inodes[inode].direct[i-1]
                for j in range(16):
                    if ba[sec*512+j*32] == 0:
                        print("COND 2", sec)
                        ba[sec*512+j*32:sec*512+j*32+32] = data
                        break
                else:
                    sec = 546 + fs.find_sector()
                    print("COND 3", sec)
                    if sec == -1: raise Exception("Not enough sectors")
                    fs.inodes[inode].direct[i] = sec
                    print("WRITE")
                    ba[sec*512:sec*512+32] = data
                    break
                break
    else:
        # TODO: write expanding to indirect nodes
        pass


if __name__ == "__main__":
    import os
    n = "stuff/fsTest/"+input("fsTest name: ")+"/"
    btp = input("Bootloader: ")

    data = bytearray(16*1024*1024)
    fs = FS(4096)

    if btp != "":
        with open(btp, "rb") as bl:
            bootloader = bytearray(bl.read())
            bootloader.extend([0] * (512 - len(bootloader)))
            data[:512] = bootloader
    
    # root directory
    fs.inodes[0].type = 2
    # ==============

    def dir_process(dir):
        print("New directory:", dir)
        create_dir(data, fs, dir)

        files = os.listdir(n+dir)
        dir += "/"
        for i in files:
            if os.path.isfile(n+dir+i):
                print("New file:", dir+i)
                create_file(data, fs, dir+i, n+dir+i)
            else:
                dir_process(dir+i)


    files = os.listdir(n)
    for i in files:
        if os.path.isfile(n+i):
            create_file(data, fs, i, n+i)
        else:
            dir_process(i)
    

    for i, inode in enumerate(fs.inodes):
        sind = inode.serialize()
        data[512+i*64:512+i*64+64] = sind

    data[514*512:546*512] = fs.sectors_bitmap

    print(sum(data))

    with open("usr/disk.img", "wb") as disk:
        disk.write(data)