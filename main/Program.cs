/*
It is just a launcher for my VM.
*/

Console.WriteLine("Which test to run?");
string num = Console.ReadLine();

Disk disk = new Disk(64 * 1024 * 1024 / 512);

// --Just for hiding real path--
string baseDir = AppDomain.CurrentDomain.BaseDirectory;
baseDir = baseDir.Substring(0, baseDir.Length-23);  // Removing 'main\bin\Debug\net10.0\' at end
string fullPath = Path.Combine(baseDir, "stuff\\test\\" + num + "\\iso", "disk.iso");
// -- --

disk.LoadFromFile(fullPath);

VirtualMachine vm = new VirtualMachine(disk);