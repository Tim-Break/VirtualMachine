_start:
    lea r2, success
    lea r3, fail

    mov r7, 1               ; Answer
    mov r0, 0xA1234567      ; Test 32-bit number
    mov r1, 0               ; Counter

    call find_zero

    cmp r1, r7
    jz scc
    mov r0, r3
scc:
    mov r0, r2
    call uart_print
    halt

find_zero:
    and r0, 0x80000000      ; bitmask
    jz fzret
    shl r0, 1
    add r1, 1
    jmp find_zero
fzret:
    ret

uart_print:
    load r1, r0
    and r1, 0xFF
    add r0, 1
    cmp r1, 0
    jz upret
    call uart_putc
    jmp uart_print
upret:
    ret

uart_putc:
    out 0x3F8, r1
    ret

success:
    db "Success!", b0
fail:
    db "Fail!", b0