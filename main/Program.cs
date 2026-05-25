/*
It is just a launcher for my VM.
*/


Disk disk = new Disk(64 * 1024 * 1024 / 512);

// --Just for hiding real path--
string baseDir = AppDomain.CurrentDomain.BaseDirectory;
baseDir = baseDir.Substring(0, baseDir.Length-23);  // Removing 'main\bin\Debug\net10.0\' at end
string fullPath = Path.Combine(baseDir, "stuff\\test\\" + "0" + "\\iso", "disk.iso");
// -- --

disk.LoadFromFile(fullPath);

VirtualMachine vm = new VirtualMachine(disk);