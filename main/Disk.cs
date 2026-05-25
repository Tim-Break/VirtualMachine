public class Disk
{
    private byte[] data;
    public const int SectorSize = 512;


    public Disk(int size)
    {
        data = new byte[SectorSize * size];
    }


    public void ReadSector(int sectorIdx, byte[] buffer, int offset)
    {
        int start = sectorIdx * SectorSize;
        Array.Copy(data, start, buffer, offset, SectorSize);
    }

    public void WriteSector(int sectorIdx, byte[] buffer, int offset)
    {
        int start = sectorIdx * SectorSize;
        Array.Copy(buffer, offset, data, start, SectorSize);
    }

    public void SaveToFile(string fp)
    {
        File.WriteAllBytes(fp, data);
    }
    public void LoadFromFile(string fp)
    {
        data = File.ReadAllBytes(fp);
    }
}