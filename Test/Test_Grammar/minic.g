G[ program ];

program ::= definition-list ;

definition-list ::=
    definition-list definition |
    definition;

definition ::=
    variable-definition |
    function-definition;

variable-definition ::=
    type-indicator ID SEM |
    type-indicator ID RSB NUMBER LSB SEM;

type-indicator ::= INT | FLOAT | VOID;

function-definition ::= type-indicator ID LP parameters RP compound-stmt;

parameters ::= 
    parameter-list | 
    VOID;

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
     IF  LP expression RP  statement |
     IF  LP expression RP statement  ELSE  statement;

dowhile-stmt ::=
    DO statement WHILE  LP  expression RP   SEM;

return-stmt ::=
    RETURN  SEM |
    RETURN expression  SEM;

expression ::=
    variable ASSIGN expression |
    simple-expression;

variable ::=
    ID |
    ID LSB expression RSB;

simple-expression ::=
    additive-expression relop additive-expression |
    additive-expression;

relop ::= LTE | LT | GT | GTE | EQ | NE;

additive-expression ::=
    additive-expression addop term |
    term;

addop ::= PLUS | MINUS;

term ::=
    term mulop factor |
    factor;

mulop ::= MUL | DIV | MOD;

factor ::=
    LP expression RP |
    variable |
    call |
    NUMBER;

call ::= ID LP arguments RP;

arguments ::=
    argument-list |
    EMPTY;

argument-list ::=
    argument-list COM expression |
    expression;


non-terminal {
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