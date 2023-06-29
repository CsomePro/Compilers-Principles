G[program];

program ::= stmt-sequence <prog,0>;

stmt-sequence ::=
    stmt-sequence SEM statement <stmt,0> |
    statement ;

statement ::=
    if-stmt |
    repeat-stmt |
    assign-stmt |
    read-stmt |
    write-stmt;

if-stmt ::=
    IF exp THEN stmt-sequence END <if_no_else,0>|
    IF exp THEN stmt-sequence ELSE stmt-sequence END <if_stmt,0>;

repeat-stmt ::= REPEAT stmt-sequence UNTIL exp <repeat,0>;

assign-stmt ::= ID ASSIGN exp <assign,0>;

read-stmt ::= READ ID <read,0>;

write-stmt ::= WRITE exp <write,0>;

exp ::=
    simple-exp comparison-op simple-exp <exp,0> |
    simple-exp;

comparison-op ::= LT | EQ;

simple-exp ::=
    simple-exp addop term <exp,0> |
    term;

addop ::= PLUS | MINUS;

term ::=
    term mulop factor <exp,0> |
    factor;

mulop ::= MUL | DIV;

factor ::=
    LP exp RP <factor_lp_rp,0> |
    NUMBER <factor,0> |
    ID <factor,0> ;

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
