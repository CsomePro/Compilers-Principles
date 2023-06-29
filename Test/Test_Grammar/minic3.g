G[ program ];

program ::= definition-list <program,1>;

definition-list ::=
    definition-list definition <def,2> |
    definition ;

definition ::=
    type-indicator ID variable-definition-tmp |
    type-indicator ID function-definition-tmp ;

variable-definition-tmp ::=
    SEM <var-def,3> |
    RSB NUMBER LSB SEM <var-def,6>;

function-definition-tmp ::=
    LP VOID <param,1> RP compound-stmt <func-def,6> |
    LP VOID ID <param,2> RP compound-stmt <func-def,6> |
    LP VOID ID LSB RSB <param,4> RP compound-stmt <func-def,6> |
    LP VOID ID <param,2> COM parameters <param,3> RP compound-stmt <func-def,6> |
    LP VOID ID LSB RSB <param,4> COM parameters <param,3> RP compound-stmt <func-def,6> |
    LP type-indicator-none-void ID <param,2> RP compound-stmt <func-def,6> |
    LP type-indicator-none-void ID LSB RSB <param,4> RP compound-stmt <func-def,6> |
    LP type-indicator-none-void ID <param,2> COM parameters <param,3> RP compound-stmt <func-def,6> |
    LP type-indicator-none-void ID LSB RSB <param,4> COM parameters <param,3> RP compound-stmt <func-def,6> ;

variable-definition ::=
    type-indicator ID SEM <var-def,3> |
    type-indicator ID LSB NUMBER RSB SEM <var-def,6> ;

function-definition ::=
    type-indicator ID function-definition-tmp;

type-indicator ::= INT | FLOAT | VOID;

type-indicator-none-void ::= INT | FLOAT;

parameters ::=
    parameter-list ;

parameter-list ::=
    parameter-list COM parameter <param,3> |
    parameter <param,1> ;

parameter ::=
    type-indicator ID <param,2> |
    type-indicator ID LSB RSB <param,4> ;

compound-stmt ::=
    OB local-definitions statement-list CB <compound,4> |
    OB statement-list CB <compound,3> |
    OB local-definitions CB <compound,3> |
    OB CB <compound,2> ;

local-definitions ::= variable-definition local-definitions <local-def,2> | variable-definition ;

statement-list ::= statement statement-list <stmt-list,2> | statement ;

statement ::=
    expression-stmt |
    compound-stmt |
    condition-stmt |
    dowhile-stmt |
    return-stmt;

expression-stmt ::=
    expression SEM <exp-sem,2> |
    SEM <exp-sem,1> ;

condition-stmt ::=
     IF  LP expression RP statement <if,5> |
     IF  LP expression RP statement  ELSE  statement <if,7> ;

dowhile-stmt ::=
    DO statement WHILE  LP  expression RP SEM <while,7>;

return-stmt ::=
    RETURN SEM <return,2> |
    RETURN expression SEM <return,3> ;

expression ::=
    ID <var,1> ASSIGN expression <exp,3> |
    ID variable-tmp ASSIGN expression <exp,3> |
    ID simple-expression-cut-id <exp,1> |
    simple-expression-nid <exp,1>;

variable ::=
    ID <var,1> |
    ID LSB expression RSB <var, 4>;

variable-tmp ::=
    LSB expression RSB <var,4> ;

simple-expression ::=
    additive-expression relop additive-expression <exp,3> |
    additive-expression <exp,1> ;

simple-expression-nid ::=
    additive-expression-nid relop additive-expression <exp,3> |
    additive-expression-nid <exp,1> ;

simple-expression-cut-id ::=
    additive-expression-cut-id relop additive-expression <exp,3> |
    additive-expression-cut-id <exp,1> ;

relop ::= LTE | LT | GT | GTE | EQ | NE;

additive-expression ::=
    additive-expression addop term <exp,3> |
    term <exp,1>;

additive-expression-nid ::=
    term-nid addop term <exp,3> |
    term-nid <exp,1>;

additive-expression-cut-id ::=
    term-cut-id addop term <exp,3> |
    term-cut-id <exp,1>;

addop ::= PLUS | MINUS;

term ::=
    term mulop factor <exp,3> |
    factor <exp,1>;

term-nid ::=
    factor-nid mulop factor <exp,3> |
    factor-nid <exp,1> ;

term-cut-id ::=
    factor-cut-id mulop factor <exp,3> |
    factor-cut-id <exp,1> ;

mulop ::= MUL | DIV | MOD;

factor ::=
    LP expression RP <factor,3> |
    ID <var,1> <factor,1> |
    ID variable-tmp <factor,1> |
    ID call-tmp <factor,1> |
    NUMBER <factor,1> ;

factor-cut-id ::=
    <var,1> <factor,1> |
    variable-tmp <factor,1> |
    call-tmp <factor,1> ;

factor-nid ::=
    LP expression RP <factor,3> |
    NUMBER <factor,1> ;


call ::=
    ID LP RP <call,3> |
    ID LP arguments RP <call,4> ;

call-tmp ::=
    LP RP <call,3> |
    LP arguments RP <call,4> ;

arguments ::=
    argument-list <args,1> ;

argument-list ::=
    argument-list COM expression <args,3> |
    expression <args,1> ;


non-terminal {
function-definition-tmp
variable-definition-tmp
definition-list
statement
factor
local-definitions
expression-stmt
call
compound-stmt
mulop
parameter
variable
function-definition
additive-expression
addop
type-indicator
parameters
arguments
parameter-list
dowhile-stmt
expression
program
definition
argument-list
return-stmt
statement-list
condition-stmt
relop
simple-expression
term
variable-definition
};

terminal {
IF
ELSE
INT
FLOAT
RETURN
VOID
DO
WHILE
PLUS
MINUS
MUL
DIV
MOD
LT
LTE
EQ
GT
GTE
NE
SEM
ASSIGN
COM
LP
RP
LSB
RSB
OB
CB
ID
NUMBER
skip
skip
};