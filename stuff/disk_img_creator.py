SECTOR_CNT = 64 * 1024 * 1024 // 512
SECTOR_SIZE = 512
KERNEL_SECTOR_CNT = 5

def create_disk_img(bootloader_path,kernel_path,output_path):
    with open(output_path, "wb") as disk:
        data = bytearray(SECTOR_CNT * SECTOR_SIZE)
        bootloader = bytearray()
        kernel = bytearray()

        with open(bootloader_path, "rb") as bl:
            bootloader = bl.read()
        with open(kernel_path, "rb") as kn:
            kernel = kn.read()
        
        bootloader = bootloader + bytearray(SECTOR_SIZE - len(bootloader))
        kernel = kernel + bytearray(SECTOR_SIZE * KERNEL_SECTOR_CNT - len(kernel))

        data[:SECTOR_SIZE] = bootloader
        data[SECTOR_SIZE:SECTOR_SIZE+SECTOR_SIZE*KERNEL_SECTOR_CNT] = kernel

        disk.write(data)


if __name__ == "__main__":
    bootloader_path = input("Compiled bootloader path: ")
    kernel_path = input("Compiled kernel path: ")
    output_path = input("ISO File path: ")
    create_disk_img(bootloader_path,kernel_path,output_path)