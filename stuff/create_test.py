def prep_test():
    BOOTLOADER_TEMPLATE = """_start:
; Preparing read operation

    mov r0, 1
    out 0x1F0, r0

    mov r0, 0x1200
    out 0x1F2, r0

    mov r0, 5       ; KERNEL_SECTORS CNT
    out 0x1F3, r0

; Initializing read operation

    mov r0, 0x20
    out 0x1F1, r0

; Go to kernel code at 0x1200

    mov r0, 0x1200
    jmp r0"""
    KERNEL_TEMPLATE = """_start:
; Kernel start point
    halt"""
    import os
    nms = os.listdir("stuff/test/")
    if len(nms) > 0:
        nms.sort()
        test_num = int(nms[-1]) + 1
    else:
        test_num = 0

    # Create test dir
    os.mkdir(f"stuff/test/{test_num}")

    # Create asm dir
    os.mkdir(f"stuff/test/{test_num}/asm")

    # Create bootloader.asm & kernel.asm
    with open(f"stuff/test/{test_num}/asm/bootloader.asm","w") as bl:
        bl.write(BOOTLOADER_TEMPLATE)
    
    with open(f"stuff/test/{test_num}/asm/kernel.asm","w") as kn:
        kn.write(KERNEL_TEMPLATE)
    
    # Create bin dir
    os.mkdir(f"stuff/test/{test_num}/bin")

    # Create iso dir
    os.mkdir(f"stuff/test/{test_num}/img")


def build_test(test_num):
    from asm_compiler import build_file
    from stuff.disk_img_creator import create_disk_img

    # Build bootloader.asm
    build_file(f"stuff/test/{test_num}/asm/bootloader.asm",
               f"stuff/test/{test_num}/bin/bootloader.bin")

    # Build kernel.asm
    build_file(f"stuff/test/{test_num}/asm/kernel.asm",
               f"stuff/test/{test_num}/bin/kernel.bin")

    # Creating disk.img
    create_disk_img(f"stuff/test/{test_num}/bin/bootloader.bin",
                    f"stuff/test/{test_num}/bin/kernel.bin",
                    f"stuff/test/{test_num}/img/disk.img")


if __name__ == "__main__":
    action = input("Prepare or Build test? (p/b) ")
    if action.lower() == "p":
        prep_test()
    elif action.lower() == "b":
        test_num = int(input("Which test you want to build? "))
        build_test(test_num)