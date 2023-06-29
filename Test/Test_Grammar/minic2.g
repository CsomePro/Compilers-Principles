G[ program ];

program ::= definition-list ;

definition-list ::=
    definition-list definition |
    definition ;

definition ::=
    type-indicator ID variable-definition-tmp |
    type-indicator ID function-definition-tmp ;

variable-definition-tmp ::=
    SEM |
    RSB NUMBER LSB SEM ;

function-definition-tmp ::=
    LP VOID RP compound-stmt |
    LP VOID ID RP compound-stmt |
    LP VOID ID COM parameters RP compound-stmt |
    LP type-indicator-none-void ID RP compound-stmt |
    LP type-indicator-none-void ID COM parameters RP compound-stmt ;

variable-definition ::=
    type-indicator ID SEM |
    type-indicator ID RSB NUMBER LSB SEM ;

function-definition ::=
    type-indicator ID LP VOID RP compound-stmt |
    type-indicator ID LP VOID ID RP compound-stmt |
    type-indicator ID LP VOID ID COM parameters RP compound-stmt |
    type-indicator ID LP type-indicator-none-void ID RP compound-stmt |
    type-indicator ID LP type-indicator-none-void ID COM parameters RP compound-stmt ;

type-indicator ::= INT | FLOAT | VOID;

type-indicator-none-void ::= INT | FLOAT;

parameters ::=
    parameter-list ;

parameter-list ::=
    parameter-list COM  parameter |
    parameter;

parameter ::=
    type-indicator ID |
    type-indicator ID LSB RSB ;

compound-stmt ::=  OB  local-definitions statement-list  CB ;

local-definitions ::= local-definitions variable-definition |  EMPTY ;

statement-list ::= statement-list statement |  EMPTY ;

statement ::=
    expression-stmt |
    compound-stmt |
    condition-stmt |
    dowhile-stmt |
    return-stmt;

expression-stmt ::=
    expression  SEM  |
    SEM;

condition-stmt ::=
     IF  LP expression RP statement |
     IF  LP expression RP statement  ELSE  statement;

dowhile-stmt ::=
    DO statement WHILE  LP  expression RP   SEM;

return-stmt ::=
    RETURN SEM |
    RETURN expression SEM;

expression ::=
    ID variable-tmp ASSIGN expression |
    ID simple-expression-cut-id |
    simple-expression-nid;

variable ::=
    ID |
    ID LSB expression RSB;

variable-tmp ::=
    EMPTY |
    LSB expression RSB;

simple-expression ::=
    additive-expression relop additive-expression |
    additive-expression;

simple-expression-nid ::=
    additive-expression-nid relop additive-expression |
    additive-expression-nid;

simple-expression-cut-id ::=
    additive-expression-cut-id relop additive-expression |
    additive-expression-cut-id;

relop ::= LTE | LT | GT | GTE | EQ | NE;

additive-expression ::=
    additive-expression addop term |
    term;

additive-expression-nid ::=
    term-nid addop term |
    term-nid;

additive-expression-cut-id ::=
    term-cut-id addop term |
    term-cut-id;

addop ::= PLUS | MINUS;

term ::=
    term mulop factor |
    factor;

term-nid ::=
    factor-nid mulop factor |
    factor-nid;

term-cut-id ::=
    factor-cut-id mulop factor |
    factor-cut-id;

mulop ::= MUL | DIV | MOD;

factor ::=
    LP expression RP |
    ID variable-tmp |
    ID call-tmp |
    NUMBER;

factor-cut-id ::=
    ID variable-tmp |
    ID call-tmp;

factor-nid ::=
    LP expression RP |
    NUMBER;

call ::= ID LP arguments RP;
call-tmp ::= LP arguments RP;

arguments ::=
    argument-list |
    EMPTY;

argument-list ::=
    argument-list COM expression |
    expression;


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