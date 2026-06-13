;!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
;!I STARTED WRITING A COMPILER FOR A C-LIKE LANGUAGE, SO I JUST USE OLD FOR NEW TEST!
;!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

_start:
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
    jmp r0