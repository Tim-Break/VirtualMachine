# VirtualMachine
An attempt to create a virtual machine for a computer network simulation game.

## How to **Run VM**
You can use `Program.cs` script from `main\`.In this case, the program will ask for the test number to be run, which is the same number that needs to be entered when building the test.

## How to **work with tests**
You can create test using `create_test.py` from `stuff/`. To do this, run this script and enter `p`. This will automatically create a new test in the `tests` folder, and `asm`, `bin` and `iso` folders will be created inside the folder with the test name (its number). The asm folder will contain a primitive bootloader and a stub kernel. When building the test, these files will be automatically compiled and written to the disk image.

You can build test immediately by running the `create_test.py` script from `stuff/`. After running the script, enter `b` and then the number of your test (the name of the folder containing the test, for exmple for test `tests/1/` you need to enter `1`). This will compile the `kernel.asm` and `bootloader.asm` scripts and create the `disk.img` file.

> [!WARNING]
> **DO NOT CREATE ANY FILES OR FOLDERS IN `stuff/tests/`. THIS MAY IMPAIR THE FUNCTIONALITY OF THE create_test.py SCRIPT.**

> [!TIP]
> If you want, you can manually compile your asm scripts and assemble them into a `disk.img`, but this is less convenient than using the tests.
> 
> Manual building `disk.img` is described here: [How to **Manually create `disk.img`**](#how-to-manually-create-diskimg).
> 
> Manual compilation is described here: [How to **Manually compile assembly files**](#how-to-manually-compile-assembly-files).

## How to **Manually create `disk.img`**
You can create a file `disk.img` using the `disk_img_creator.py` script from `stuff/`.

## How to **Manually compile assembly files**
You can compile any of your assembly files (`.asm`) using the `asm_compiler.py` script from `stuff/`. When you run the program, it will ask you for the path to your `.asm` file and the name of the compiled file (it is recommended to use the `.bin` extension). Any execution error is most likely caused by an incorrect assembly code (but this is not guaranteed `:)`).




