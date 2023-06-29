G[program];

program ::= stmt-sequence <program,1>;

stmt-sequence ::=
    stmt-sequence SEM statement <stmt,3> |
    statement ;

statement ::=
    if-stmt |
    repeat-stmt |
    assign-stmt |
    read-stmt |
    write-stmt;

if-stmt ::=
    IF exp THEN stmt-sequence END <if,5>|
    IF exp THEN stmt-sequence ELSE stmt-sequence END <if,6>;

repeat-stmt ::= REPEAT stmt-sequence UNTIL exp <repeat,4>;

assign-stmt ::= ID ASSIGN exp <assign,3>;

read-stmt ::= READ ID <read,2>;

write-stmt ::= WRITE exp <write,2>;

exp ::=
    simple-exp comparison-op simple-exp <exp,3> |
    simple-exp;

comparison-op ::= LT | EQ;

simple-exp ::=
    simple-exp addop term <simple,3> |
    term;

addop ::= PLUS | MINUS;

term ::=
    term mulop factor <term,3> |
    factor;

mulop ::= MUL | DIV;

factor ::=
    LP exp RP <factor,3> |
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
