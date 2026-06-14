cmds = {
    "mov_i" : 0x01,
    "mov_r" : 0x02,

    "load" : 0x04,
    "store" : 0x05,

    "add_r" : 0x10,
    "sub_r" : 0x11,
    "mul_r" : 0x12,
    "div_r" : 0x13,

    "shl_r" : 0x14,
    "shr_r" : 0x15,

    "and_r" : 0x16,
    "or_r"  : 0x17,
    "xor_r" : 0x18,

    "cmp_r" : 0x19,

    "add_i" : 0x1A,
    "sub_i" : 0x1B,
    "mul_i" : 0x1C,
    "div_i" : 0x1D,

    "shl_i" : 0x1E,
    "shr_i" : 0x1F,

    "and_i" : 0x20,
    "or_i"  : 0x21,
    "xor_i" : 0x22,

    "cmp_i" : 0x23,

    "not" : 0x24,

    "push" : 0x2D,
    "pop" : 0x2E,

    "jmp_r" : 0x30,
    "jz_r" : 0x31,
    "jnz_r" : 0x32,

    "jmp_a" : 0x37,
    "jz_a" : 0x38,
    "jnz_a" : 0x39,

    "call" : 0x34,
    "ret" : 0x35,

    "lea" : 0x40,

    "int" : 0x50,
    "iret" : 0x51,

    "in" : 0x60,
    "out" : 0x61,

    "halt" : 0xFF
}


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


def parse_marker(line:str):
    mrk = ""

    pmrk = False
    while len(line) >= 1:
        if line[0].isalnum() or line[0] in ("_", ".", "-"):
            pmrk = True
            mrk += line[0]
        elif pmrk:
            break
        line = line[1:]
    
    return mrk


def parse_cmd(line:str):
    cmd = ""

    pcmd = False
    while len(line) >= 1:
        if line[0].isalnum():
            pcmd = True
            cmd += line[0]
        elif pcmd:
            break
        line = line[1:]
    
    args = []

    while len(line) >= 1:
        if len(line) >= 2 and line[0] == "r" and line[1].isdigit():
            args.append(("reg", int(line[1])))
            line = line[1:]
        elif len(line) >= 2 and line[0] == "b" and line[1].isdigit():
            num = ""
            line = line[1:]
            while len(line) >= 1 and line[0].isdigit():
                num += line[0]
                line = line[1:]
            args.append(("byt", [int(num)]))
        elif line[0].isalpha() or line[0] in ("_"):
            mrk = ""
            while len(line) >= 1 and (line[0].isalnum() or line[0] in ("_", ".", "-")):
                mrk += line[0]
                line = line[1:]
            args.append(("mrk", mrk))
        elif len(line) >= 3 and line[0] == "0" and line[1] in ("x","b"):
            sys = (16 if line[1] == "x" else 2)
            line = line[2:]
            num = ""
            while len(line) >= 1 and (line[0].isdigit() or line[0] in "ABCDEF"):
                num += line[0]
                line = line[1:]
            args.append(("num", int(num, sys)))
        elif line[0].isdigit() or line[0] == "-":
            num = line[0]
            line = line[1:]
            while len(line) >= 1 and line[0].isdigit():
                num += line[0]
                line = line[1:]
            args.append(("num", int(num)))
        elif line[0] == '"':
            value = ""
            line = line[1:]
            while len(line) >= 1 and line[0] != '"':
                if line[0] == "\\":
                    line = line[1:]
                    if line[0] in ("'",'"'):
                        value += line[0]
                        line = line[1:]
                    elif line[0] == "n":
                        value += "\n"
                        line = line[1:]
                    elif line[0] == "t":
                        value += "\t"
                        line = line[1:]
                    elif line[0] == "\\":
                        value += "\\"
                        line = line[1:]
                else:
                    value += line[0]
                    line = line[1:]
            args.append(("byt", list(value.encode("ascii"))))
        elif line[0] == "'":
            value = ""
            line = line[1:]
            while len(line) >= 1 and line[0] != '"':
                if line[0] == "\\":
                    line = line[1:]
                    if line[0] in ("'",'"'):
                        value += line[0]
                        line = line[1:]
                    elif line[0] == "n":
                        value += "\n"
                        line = line[1:]
                    elif line[0] == "t":
                        value += "\t"
                        line = line[1:]
                    elif line[0] == "\\":
                        value += "\\"
                        line = line[1:]
                else:
                    value += line[0]
                    line = line[1:]
            args.append(("num", bytes2int32(bytearray(value.encode("ascii")))))
        line = line[1:]
    
    return cmd, args


def compile(text:str):
    out = bytearray()

    markers = {}
    write_markers = []

    lines = text.splitlines()
    for line in lines:
        cpos = line.find(";")
        if cpos != -1:
            line = line[:cpos]
        
        if line.find(":") == -1:
            cmd = parse_cmd(line)
            if cmd[0] == "": continue
            #print(cmd)
            if cmd[0] in ("mov","add","sub","mul","div","shl","shr","and","or","xor","cmp"):
                if cmd[1][1][0] == "reg":
                    out.extend([cmds[cmd[0]+"_r"], cmd[1][0][1], cmd[1][1][1]])
                elif cmd[1][1][0] == "num":
                    out.extend([cmds[cmd[0]+"_i"], cmd[1][0][1]] + int2bytes32(cmd[1][1][1]))
            elif cmd[0] in ("load","store"):
                out.extend([cmds[cmd[0]], cmd[1][0][1], cmd[1][1][1]])
            elif cmd[0] in ("jmp","jz","jnz"):
                if cmd[1][0][0] == "reg":
                    out.extend([cmds[cmd[0]+"_a"], cmd[1][0][1]])
                elif cmd[1][0][0] == "mrk":
                    out.append(cmds[cmd[0]+"_r"])
                    write_markers.append((len(out),len(out)+4,cmd[1][0][1]))
                    out.extend([0,0,0,0])
            elif cmd[0] in ("push","pop","not"):
                out.extend([cmds[cmd[0]], cmd[1][0][1]])
            elif cmd[0] == "lea":
                out.extend([cmds["lea"], cmd[1][0][1]])
                write_markers.append((len(out),len(out)+4,cmd[1][1][1]))
                out.extend([0,0,0,0])
            elif cmd[0] == "call":
                out.append(cmds["call"])
                write_markers.append((len(out),len(out)+4,cmd[1][0][1]))
                out.extend([0,0,0,0])
            elif cmd[0] == "int":
                out.extend([cmds["int"]] + int2bytes32(cmd[1][0][1])[:2])
            elif cmd[0] == "in":
                out.extend([cmds["in"], cmd[1][0][1]] + int2bytes32(cmd[1][1][1])[:2])
            elif cmd[0] == "out":
                out.extend([cmds["out"]] + int2bytes32(cmd[1][0][1])[:2] + [cmd[1][1][1]])
            elif cmd[0] in ("ret","iret","halt"):
                out.append(cmds[cmd[0]])
            elif cmd[0] == "db":
                for arg in cmd[1]:
                    if arg[0] == "byt":
                        out.extend(arg[1])
                    elif arg[0] == "num":
                        out.extend(int2bytes32(arg[1]))
        else:
            mrk = parse_marker(line)
            markers[mrk] = len(out)
    
    for wmrk in write_markers:
        out[wmrk[0]:wmrk[0]+4] = bytearray(int2bytes32(markers[wmrk[2]] - wmrk[1]))
    
    return out


def build_file(ifp:str, ofp:str="build.bin"):
    with open(ifp, "r") as f:
        code = f.read()
    
    ccd = bytes(compile(code))

    with open(ofp, "wb") as f:
        f.write(ccd)


if __name__ == "__main__":
    build_file(input("Code path: "), input("Output path: "))