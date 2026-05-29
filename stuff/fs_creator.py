

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
        for i in range(10):
            out.extend(int2bytes32(self.direct[i]))
        out.extend(int2bytes32(self.indirect1))
        out.extend(int2bytes32(self.indirect2))
        out.extend([0]*3)
        return out

    def __repr__(self):
        return f"Inode:\n\tType: {self.type}\n\tSize: {self.size}\n\tDirect: {self.direct}\n\tIndirect 1: {self.indirect1}\n\tIndirect 2: {self.indirect2}"
    

class FS:
    def __init__(self, inode_cnt):
        self.inodes = [Inode() for _ in range(inode_cnt)]
        self.sectors_bitmap = bytearray(32)

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


data = bytearray(64*1024*1024)
fs = FS(4096)


# root directory
fs.inodes[0].type = 2
# ==============


def create_file(ba: bytearray, fs: FS, fp: str):
    inode = fs.find_inode()
    print("Inode",inode)
    if inode == -1: raise Exception("Not enough inodes")
    fs.inodes[inode].type = 1
    with open(fp, "rb") as f:
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


def create_dir(ba: bytearray, fs: FS, dp: str):
    inode = fs.find_inode()
    if inode == -1: raise Exception("Not enough inodes")
    fs.inodes[inode].type = 2


def find_entry_in_dir(ba: bytearray, fs: FS, inode: int, entry: bytearray):
    for i in fs.inodes[inode].direct:
        val = ba[512*i:512*i+512]
        for j in range(0,512,32):
            for k in range(28):
                if val[j+k] != entry[j]:
                    break
            else:
                return bytes2int32(val[j+k+28:j+k+32])
    for n in range(0,128,4):
        i = bytes2int32(ba[fs.inodes[inode].indirect1+n:fs.inodes[inode].indirect1+n+4])
        val = ba[512*i:512*i+512]
        for j in range(0,512,32):
            for k in range(28):
                if val[j+k] != entry[j]:
                    break
            else:
                return bytes2int32(val[j+k+28:j+k+32])
    for n in range(0,128,4):
        i = bytes2int32(ba[fs.inodes[inode].indirect2+n:fs.inodes[inode].indirect2+n+4])
        val = ba[512*i:512*i+512]
        for j in range(0,512,32):
            for k in range(28):
                if val[j+k] != entry[j]:
                    break
            else:
                return bytes2int32(val[j+k+28:j+k+32])
    return -1


def add_object_to_dir(ba: bytearray, fs: FS, path: str, tinode: int):
    path_splitted = path.split("/")
    if len(path_splitted) < 2: return
    path_bytes = [bytearray(i.encode("ascii")) for i in path_splitted]

    inode = 0
    for i in range(len(path_bytes)-1):
        if len(path_bytes) > 28:
            path_bytes[i] = path_bytes[:28]
        else:
            path_bytes[i].extend([0]*28-len(path_bytes))
        if inode == -1: raise Exception("Directory is not exists!")
        inode = find_entry_in_dir(ba, fs, inode, path_bytes[i])
    
    data = path_bytes[-1]
    data.extend(int2bytes32(tinode))
    fs.inodes[inode].size += 32
    # TODO: writedirectory expander

    


print("start 1")
create_file(data, fs, "IMG_20260519_213833.webp")

print("start 2")
create_dir(data, fs, "usr")

print(fs.inodes[0])
print(fs.inodes[1])