_start:
    ; Preparing read operation to read inode table

    mov r0, 1       ; index of first sector to read
    out 0x1F0, r0

    mov r0, 0x1200  ; ram address
    out 0x1F2, r0

    mov r0, 512     ; how many sectors does table occupied
    out 0x1F3, r0

    ; Initializing read operation

    mov r0, 0x20
    out 0x1F1, r0

    ; Now there is inode table in ram at 0x1200

    lea r0, kernel_path
    call find_inode
    ; now there is kernel inode index in r0
    ; TODO: write kernel reading to ram and executing it

find_inode:
    mov r1, 0       ; target inode index
fi_loop:
    ; TODO: write inode finding

kernel_path:
    db "sys/kernel.bin"