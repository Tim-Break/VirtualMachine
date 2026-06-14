jmp _start
_var_a: ;Declaration of variable a
db 0
_var_b: ;Declaration of variable b
db 0
_start:
mov r1, 10      ;Integer
lea r2, _var_a
store r2, r1
mov r1, 10      ;Integer
lea r2, _var_b
store r2, r1
;IF START
lea r1, _var_b  ;ST Variable use
load r1, r1     ;END Variable use
mov r2, r1
lea r1, _var_a  ;ST Variable use
load r1, r1     ;END Variable use
sub r1, r2      ;ST BinOp ==
mov r2, r1
mul r1, -1
or r2, r1
shl r2, 31
mov r1, 1
sub r1, r2      ;END BinOp ==
cmp r1, 1
jnz _if-after_0
;ST Assignation of variable a
mov r1, 1       ;Integer
mov r2, r1
lea r1, _var_a  ;ST Variable use
load r1, r1     ;END Variable use
add r1, r2      ;BinOp +
lea r2, _var_a
store r2, r1    ;END Assignation of variable a
_if-after_0:    ;IF END
; CUSTOM CODE WHICH I WROTE MANUALLY TO SEE THE VALUE OF VARIABLE 'a'
lea r1, _var_a
load r1, r1
halt