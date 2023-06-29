G[program];

if-stmt_Fo1VG ::= END <if_no_else,0>;
if-stmt_Fo1VG ::= ELSE stmt-sequence END <if_stmt,0>;
if-stmt ::= IF exp THEN stmt-sequence if-stmt_Fo1VG;
repeat-stmt ::= REPEAT stmt-sequence UNTIL exp <repeat,0>;
assign-stmt ::= ID ASSIGN exp <assign,0>;
read-stmt ::= READ ID <read,0>;
write-stmt ::= WRITE exp <write,0>;
exp_1qezL ::= comparison-op simple-exp <exp,0>;
exp_1qezL ::= <EPS>;
exp ::= simple-exp exp_1qezL;
comparison-op ::= LT;
comparison-op ::= EQ;
simple-exp ::= term simple-exp_Nuxhq;
addop ::= PLUS;
addop ::= MINUS;
mulop ::= MUL;
mulop ::= DIV;
factor ::= LP exp RP <factor_lp_rp,0>;
factor ::= NUMBER <factor,0>;
factor ::= ID <factor,0>;
simple-exp_Nuxhq ::= addop term <exp,0> simple-exp_Nuxhq;
simple-exp_Nuxhq ::= <EPS>;
statement ::= IF exp THEN stmt-sequence if-stmt_Fo1VG;
statement ::= WRITE exp <write,0>;
statement ::= READ ID <read,0>;
statement ::= ID ASSIGN exp <assign,0>;
statement ::= REPEAT stmt-sequence UNTIL exp <repeat,0>;
stmt-sequence ::= IF exp THEN stmt-sequence if-stmt_Fo1VG stmt-sequence_mdNP4;
stmt-sequence ::= WRITE exp <write,0> stmt-sequence_mdNP4;
stmt-sequence ::= READ ID <read,0> stmt-sequence_mdNP4;
stmt-sequence ::= ID ASSIGN exp <assign,0> stmt-sequence_mdNP4;
stmt-sequence ::= REPEAT stmt-sequence UNTIL exp <repeat,0> stmt-sequence_mdNP4;
stmt-sequence_mdNP4 ::= SEM statement <stmt,0> stmt-sequence_mdNP4;
stmt-sequence_mdNP4 ::= <EPS>;
term ::= LP exp RP <factor_lp_rp,0> term_t4hiD;
term ::= NUMBER <factor,0> term_t4hiD;
term ::= ID <factor,0> term_t4hiD;
term_t4hiD ::= mulop factor <exp,0> term_t4hiD;
term_t4hiD ::= <EPS>;
program ::= IF exp THEN stmt-sequence if-stmt_Fo1VG stmt-sequence_mdNP4 <prog,0>;
program ::= WRITE exp <write,0> stmt-sequence_mdNP4 <prog,0>;
program ::= READ ID <read,0> stmt-sequence_mdNP4 <prog,0>;
program ::= ID ASSIGN exp <assign,0> stmt-sequence_mdNP4 <prog,0>;
program ::= REPEAT stmt-sequence UNTIL exp <repeat,0> stmt-sequence_mdNP4 <prog,0>;

non-terminal {
term_t4hiD
write-stmt
program
stmt-sequence_mdNP4
read-stmt
if-stmt_Fo1VG
simple-exp
mulop
addop
simple-exp_Nuxhq
term
if-stmt
exp_1qezL
assign-stmt
factor
exp
repeat-stmt
statement
stmt-sequence
comparison-op
};

terminal {
END
REPEAT
LP
UNTIL
IF
ELSE
MUL
NUMBER
SEM
DIV
ID
READ
PLUS
LT
MINUS
THEN
WRITE
<EPS>
ASSIGN
EQ
RP
};

