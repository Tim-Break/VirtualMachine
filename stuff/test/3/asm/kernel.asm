_start:
    mov r1, 4096
    mov r0, 0
    call loop
    halt

loop:
    add r2, 1 ; Eating time
    sub r2, 1 ; Eating time
    add r2, 1 ; Eating time
    sub r2, 1 ; Eating time

    add r0, 1
    cmp r0, r1
    jz ret
    jmp loop
ret:
    ret