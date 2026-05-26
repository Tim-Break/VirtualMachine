public class VirtualMachine
{
    private DateTime date = new DateTime(2026, 1, 1, 0, 0, 0);

    private int ramsize;
    private byte[] ram;

    public int[] rgs = [0,0,0,0,0,0,0,0];

    private int ip = 0;
    private int sp = 0;

    private byte flags = 0; // ()()()()()()(SF)(ZF)

    private Disk disk;

    private uint diskLBA;
    private uint diskMemAddr;
    private uint diskSectorCount;


    private Dictionary<ushort, Action<uint>> portWriters = new();
    private Dictionary<ushort, Func<uint>> portReaders = new();


    public VirtualMachine(Disk disk, int ramsize = 16_777_216)
    {
        this.ramsize = ramsize;
        ram = new byte[ramsize];
        sp = ramsize;

        this.disk = disk;

        SetupDiskPorts(disk);
        portWriters[0x3F8] = (val) => Console.Write((char)(val & 0xFF));

        portReaders[0xFC0] = () => (uint)GetTime();     // Time port

        BootFromDisk();
    }


    private void SetupDiskPorts(Disk disk)
    {
        portWriters[0x1F0] = (val) => diskLBA = val;
        portWriters[0x1F2] = (val) => diskMemAddr = val;
        portWriters[0x1F3] = (val) => diskSectorCount = val & 0xFF;
        portWriters[0x1F1] = (val) => {
            byte cmd = (byte)(val & 0xFF);
            if (cmd == 0x20) // READ SECTORS
            {
                byte[] sectorBuf = new byte[Disk.SectorSize];
                for (int i = 0; i < diskSectorCount; i++)
                {
                    disk.ReadSector((int)(diskLBA + i), sectorBuf, 0);
                    Array.Copy(sectorBuf, 0, ram, (int)(diskMemAddr + i * Disk.SectorSize), Disk.SectorSize);
                }
            }
            else if (cmd == 0x30) // WRITE SECTORS
            {
                byte[] sectorBuf = new byte[Disk.SectorSize];
                for (int i = 0; i < diskSectorCount; i++)
                {
                    Array.Copy(ram, (int)(diskMemAddr + i * Disk.SectorSize), sectorBuf, 0, Disk.SectorSize);
                    disk.WriteSector((int)(diskLBA + i), sectorBuf, 0);
                }
            }
        };
    }


    private long GetTime()
    {
        return (long)(date - DateTime.UtcNow).TotalMilliseconds;
    }
    

    void SetZF(bool value)
    {
        flags &= 0b11111110;
        if (value) flags |= 0b00000001;
    }
    void SetSF(bool value)
    {
        flags &= 0b11111101;
        if (value) flags |= 0b00000010;
    }

    bool IsZF()
    {
        return (flags & 0b00000001) > 0;
    }
    bool IsSF()
    {
        return (flags & 0b00000010) > 0;
    }


    byte Execute()
    {
        CMD opc = (CMD)ram[ip];
        //Console.WriteLine(opc);

        switch (opc)
        {
            case CMD.mov_r:
            {
                byte r1 = ram[ip+1];
                byte r2 = ram[ip+2];
                rgs[r1] = rgs[r2];
                ip += 3;
                return 255;
            }

            case CMD.mov_i:
            {
                byte r1 = ram[ip+1];
                rgs[r1] = BitConverter.ToInt32(ram, ip+2);
                ip += 6;
                return 255;
            }

            case CMD.load:
            {
                byte r1 = ram[ip+1];
                byte r2 = ram[ip+2];
                rgs[r1] = BitConverter.ToInt32(ram, rgs[r2]);
                ip += 3;
                return 255;
            }

            case CMD.store:
            {
                byte r1 = ram[ip+1];
                byte r2 = ram[ip+2];
                BitConverter.GetBytes(rgs[r2]).CopyTo(ram, rgs[r1]);
                ip += 3;
                return 255;
            }

            case CMD.add_r:
            {
                byte r1 = ram[ip+1];
                byte r2 = ram[ip+2];
                rgs[r1] = rgs[r1] + rgs[r2];
                ip += 3;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.sub_r:
            {
                byte r1 = ram[ip+1];
                byte r2 = ram[ip+2];
                rgs[r1] = rgs[r1] - rgs[r2];
                ip += 3;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.mul_r:
            {
                byte r1 = ram[ip+1];
                byte r2 = ram[ip+2];
                rgs[r1] = rgs[r1] * rgs[r2];
                ip += 3;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.div_r:
            {
                byte r1 = ram[ip+1];
                byte r2 = ram[ip+2];
                // Exception if division by zero
                rgs[r1] = rgs[r1] / rgs[r2];
                ip += 3;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.shl_r:
            {
                byte r1 = ram[ip+1];
                byte r2 = ram[ip+2];
                rgs[r1] = rgs[r1] << rgs[r2];
                ip += 3;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.shr_r:
            {
                byte r1 = ram[ip+1];
                byte r2 = ram[ip+2];
                rgs[r1] = rgs[r1] >> rgs[r2];
                ip += 3;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.and_r:
            {
                byte r1 = ram[ip+1];
                byte r2 = ram[ip+2];
                rgs[r1] = rgs[r1] & rgs[r2];
                ip += 3;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.or_r:
            {
                byte r1 = ram[ip+1];
                byte r2 = ram[ip+2];
                rgs[r1] = rgs[r1] | rgs[r2];
                ip += 3;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.xor_r:
            {
                byte r1 = ram[ip+1];
                byte r2 = ram[ip+2];
                rgs[r1] = rgs[r1] ^ rgs[r2];
                ip += 3;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.cmp_r:
            {
                byte r1 = ram[ip+1];
                byte r2 = ram[ip+2];
                int res = rgs[r1] - rgs[r2];
                ip += 3;
                SetZF(res == 0);
                SetSF(((uint)res & 0x80000000) != 0);
                return 255;
            }
            
            case CMD.add_i:
            {
                byte r1 = ram[ip+1];
                rgs[r1] = rgs[r1] + BitConverter.ToInt32(ram, ip+2);
                ip += 6;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.sub_i:
            {
                byte r1 = ram[ip+1];
                rgs[r1] = rgs[r1] - BitConverter.ToInt32(ram, ip+2);
                ip += 6;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.mul_i:
            {
                byte r1 = ram[ip+1];
                rgs[r1] = rgs[r1] * BitConverter.ToInt32(ram, ip+2);
                ip += 6;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.div_i:
            {
                byte r1 = ram[ip+1];
                // Exception if division by zero
                rgs[r1] = rgs[r1] / BitConverter.ToInt32(ram, ip+2);
                ip += 6;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.shl_i:
            {
                byte r1 = ram[ip+1];
                rgs[r1] = rgs[r1] << BitConverter.ToInt32(ram, ip+2);
                ip += 6;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.shr_i:
            {
                byte r1 = ram[ip+1];
                rgs[r1] = rgs[r1] >> BitConverter.ToInt32(ram, ip+2);
                ip += 6;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.and_i:
            {
                byte r1 = ram[ip+1];
                rgs[r1] = rgs[r1] & BitConverter.ToInt32(ram, ip+2);
                ip += 6;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.or_i:
            {
                byte r1 = ram[ip+1];
                rgs[r1] = rgs[r1] | BitConverter.ToInt32(ram, ip+2);
                ip += 6;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.xor_i:
            {
                byte r1 = ram[ip+1];
                rgs[r1] = rgs[r1] ^ BitConverter.ToInt32(ram, ip+2);
                ip += 6;
                SetZF(rgs[r1] == 0);
                SetSF(((uint)rgs[r1] & 0x80000000) != 0);
                return 255;
            }

            case CMD.cmp_i:
            {
                byte r1 = ram[ip+1];
                int res = rgs[r1] - BitConverter.ToInt32(ram, ip+2);
                ip += 6;
                SetZF(res == 0);
                SetSF(((uint)res & 0x80000000) != 0);
                return 255;
            }
            
            case CMD.push:
            {
                byte r1 = ram[ip+1];
                sp -= 4;
                BitConverter.GetBytes(rgs[r1]).CopyTo(ram, sp);
                ip += 2;
                return 255;
            }

            case CMD.pop:
            {
                byte r1 = ram[ip+1];
                rgs[r1] = BitConverter.ToInt32(ram, sp);
                sp += 4;
                ip += 2;
                return 255;
            }

            case CMD.jmp_r:
            {
                int rel = BitConverter.ToInt32(ram, ip+1);
                ip += 5 + rel;
                return 255;
            }

            case CMD.jz_r:
            {
                int rel = BitConverter.ToInt32(ram, ip+1);
                if (IsZF())
                    ip += 5 + rel;
                else
                    ip += 5;
                return 255;
            }

            case CMD.jnz_r:
            {
                int rel = BitConverter.ToInt32(ram, ip+1);
                if (!IsZF())
                    ip += 5 + rel;
                else
                    ip += 5;
                return 255;
            }

            case CMD.jmp_a:
            {
                byte r1 = ram[ip+1];
                ip = rgs[r1];
                return 255;
            }

            case CMD.jz_a:
            {
                byte r1 = ram[ip+1];
                if (IsZF())
                    ip = rgs[r1];
                else
                    ip += 2;
                return 255;
            }

            case CMD.jnz_a:
            {
                byte r1 = ram[ip+1];
                if (!IsZF())
                    ip = rgs[r1];
                else
                    ip += 2;
                return 255;
            }

            case CMD.call:
            {
                int rel = BitConverter.ToInt32(ram, ip+1);
                sp -= 4;
                BitConverter.GetBytes(ip + 5).CopyTo(ram, sp);
                ip += 5 + rel;
                return 255;
            }

            case CMD.ret:
            {
                ip = BitConverter.ToInt32(ram, sp);
                sp += 4;
                return 255;
            }

            case CMD.lea:
            {
                byte r1 = ram[ip+1];
                int rel = BitConverter.ToInt32(ram, ip+2);
                rgs[r1] = ip + 6 + rel;
                ip += 6;
                return 255;
            }
            
            case CMD.int_:
            {
                int num = BitConverter.ToInt16(ram, ip+1);
                ip += 3;
                sp -= 4;
                BitConverter.GetBytes((uint)flags).CopyTo(ram, sp);
                sp -= 4;
                BitConverter.GetBytes(ip).CopyTo(ram, sp);
                ip = BitConverter.ToInt32(ram, num * 4);
                return 255;
            }

            case CMD.iret:
            {
                ip = BitConverter.ToInt32(ram, sp);
                sp += 4;
                flags = (byte)BitConverter.ToInt32(ram, sp);
                sp += 4;
                return 255;
            }

            case CMD.in_:
            {
                byte r1 = ram[ip+1];
                ushort port = BitConverter.ToUInt16(ram, ip+2);
                if (portReaders.TryGetValue(port, out var reader))
                    rgs[r1] = (int)reader();
                else
                    rgs[r1] = 0;
                ip+=4;
                return 255;
            }

            case CMD.out_:
            {
                ushort port = BitConverter.ToUInt16(ram, ip+1);
                byte r1 = ram[ip+3];
                if (portWriters.TryGetValue(port, out var writer))
                    writer((uint)rgs[r1]);
                ip+=4;
                return 255;
            }

            case CMD.halt:
                ip += 1;
                return 0;

            default:
                return 1;
        }
    }

    public int Run()
    {
        while (true)
        {
            byte status = Execute();
            if (status != 255)
            {
                return status;
            }
        }
    }

    public void BootFromDisk()
    {
        // BIOS
        byte[] buff = new byte[Disk.SectorSize];
        disk.ReadSector(0, buff, 0);
        Array.Copy(buff, 0, ram, 0x1000, Disk.SectorSize);

        ip = 0x1000;

        Run();
        // BIOS
    }
}
