; Printing welcome

_start:
    lea r0, welcome
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

welcome:
    db "WELCOME TO\n _____   ____    __   __\n|  _  | |    |   \\ \\ / /\n| |_| |  \\  \\     \\   /\n|_____| |____|     |_|  v5.25.1", b0