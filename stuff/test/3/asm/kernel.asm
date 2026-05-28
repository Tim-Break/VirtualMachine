_start:
    mov r0, 131072
    in r6, 0xFC0    ; Start time
    call loop
    in r7, 0xFC0    ; End time
    sub r7, r6
    halt

loop:
    add r2, 1 ; Eating time
    sub r2, 1 ; Eating time
    add r2, 1 ; Eating time
    sub r2, 1 ; Eating time

    sub r0, 1
    jz ret
    jmp loop
ret:
    ret