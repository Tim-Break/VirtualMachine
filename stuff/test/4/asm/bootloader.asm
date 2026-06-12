;!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
;!I STARTED WRITING A COMPILER FOR A C-LIKE LANGUAGE, SO I WON'T WRITE THIS MANUALLY!
;!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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
    mov r2, 0       ; symbol index
    lea r3, temp1
    fi_find_loop:
        ; CODE CODE CODE
        fi_split_loop:
            load r4, r0
            and r4, 0xFF
            
            add r0, 1
            add r2, 1

            cmp r4, '/'
            jz fi_skip_slash

            cmp r4, b0
            jz fi_end_of_path

            mov r6, r2
            add r6, r3
            store r6, r4
            jmp fi_split_loop
        fi_skip_slash:
            add r0, 1   ; skipping '/'
            add r2, 1   ; skipping '/'
        fi_end_of_path:
            ; CODE CODE CODE
        
        

error:
    out 0x3F8, 'E'
    out 0x3F8, 'R'
    out 0x3F8, 'R'
    out 0x3F8, 'O'
    out 0x3F8, 'R'
    halt

kernel_path:
    db "sys/kernel.bin", b0

temp1:
    db 0, 0, 0, 0, 0, 0, 0, b255, b255, b255