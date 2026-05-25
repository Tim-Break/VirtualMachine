; Just printing "Hello, World!\n"

_start:
    lea r0, string1
    call uart_print
    halt

uart_print:
    load r1, r0
    and r1, 0xFF
    add r0, 1
    cmp r1, 0
    jz ret
    call uart_putc
    jmp uart_print
ret:
    ret

uart_putc:
    out 0x3F8, r1
    ret

string1:
    db "Hello, World!\n", b0