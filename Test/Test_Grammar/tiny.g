G[program];

program ::= stmt-sequence;

stmt-sequence ::=
    stmt-sequence SEM statement |
    statement;

statement ::=
    if-stmt |
    repeat-stmt |
    assign-stmt |
    read-stmt |
    write-stmt;

if-stmt ::=
    IF exp THEN stmt-sequence END |
    IF exp THEN stmt-sequence ELSE stmt-sequence END;

repeat-stmt ::= REPEAT stmt-sequence UNTIL exp;

assign-stmt ::= ID ASSIGN exp;

read-stmt ::= READ ID;

write-stmt ::= WRITE exp;

exp ::=
    simple-exp comparison-op simple-exp |
    simple-exp;

comparison-op ::= LT | EQ;

simple-exp ::=
    simple-exp addop term |
    term;

addop ::= PLUS | MINUS;

term ::=
    term mulop factor |
    factor;

mulop ::= MUL | DIV;

factor ::=
    LP exp RP |
    NUMBER |
    ID;

non-terminal {
program
stmt-sequence
statement
if-stmt
repeat-stmt
assign-stmt
read-stmt
write-stmt
exp
comparison-op
simple-exp
addop
term
mulop
factor
};

terminal {
IF
ELSE
THEN
END
REPEAT
UNTIL
READ
WRITE
PLUS
MINUS
MUL
DIV
LT
EQ
SEM
ASSIGN
LP
RP
ID
NUMBER
};
