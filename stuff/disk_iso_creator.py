SECTOR_CNT = 64 * 1024 * 1024 // 512
SECTOR_SIZE = 512
KERNEL_SECTOR_CNT = 5

BOOTLOADER_PATH = input("Compiled bootloader path: ")
KERNEL_PATH = input("Compiled kernel path: ")
OUTPUT = input("ISO File path: ")

with open(OUTPUT, "wb") as disk:
    data = bytearray(SECTOR_CNT * SECTOR_SIZE)
    bootloader = bytearray()
    kernel = bytearray()

    with open(BOOTLOADER_PATH, "rb") as bl:
        bootloader = bl.read()
    with open(KERNEL_PATH, "rb") as kn:
        kernel = kn.read()
    
    bootloader = bootloader + bytearray(SECTOR_SIZE - len(bootloader))
    kernel = kernel + bytearray(SECTOR_SIZE * KERNEL_SECTOR_CNT - len(kernel))

    data[:SECTOR_SIZE] = bootloader
    data[SECTOR_SIZE:SECTOR_SIZE+SECTOR_SIZE*KERNEL_SECTOR_CNT] = kernel

    disk.write(data)