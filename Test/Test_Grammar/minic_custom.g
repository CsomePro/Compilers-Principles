G[ program ];

program ::= definition-list <program,0> ;

definition-list ::=
    definition-list definition <def,0> |
    definition <program,0> ;

definition ::=
    variable-definition |
    function-definition;

variable-definition ::=
    type-indicator ID SEM <var,0> |
    type-indicator ID LSB NUMBER RSB SEM <var,0>;

type-indicator ::= INT | FLOAT | VOID;

function-definition ::= type-indicator ID LP parameters RP compound-stmt <func,0>;

parameters ::=
    parameter-list |
    VOID;

parameter-list ::=
    parameter-list COM  parameter <param-list,0> |
    parameter ;

parameter ::=
    type-indicator ID <param,0> |
    type-indicator ID LSB RSB <param,0>;

compound-stmt ::=
    OB  local-definitions statement-list  CB <compound,0> |
    OB  local-definitions  CB  <compound,0> |
    OB  statement-list CB <compound,0> |
    OB  CB <compound,0> ;

local-definitions ::= variable-definition local-definitions <local-list,0> | variable-definition  ;

statement-list ::= statement statement-list <stmt-list,0> |  statement ;

statement ::=
    expression-stmt |
    compound-stmt |
    condition-stmt |
    dowhile-stmt |
    return-stmt;

expression-stmt ::=
    expression  SEM <exp-sem,2> |
    SEM;

condition-stmt ::=
     IF  LP expression RP  statement <if,0> |
     IF  LP expression RP statement  ELSE  statement <if,0>;

dowhile-stmt ::=
    DO statement WHILE  LP  expression RP   SEM  <while,0>;

return-stmt ::=
    RETURN  SEM <return,0> |
    RETURN expression  SEM <return,0> ;

expression ::=
    variable ASSIGN expression  <exp,0> |
    simple-expression;

variable ::=
    ID |
    ID LSB expression RSB <var,0> ;

simple-expression ::=
    additive-expression relop additive-expression <exp,0> |
    additive-expression;

relop ::= LTE | LT | GT | GTE | EQ | NE;

additive-expression ::=
    additive-expression addop term <exp,0> |
    term;

addop ::= PLUS | MINUS;

term ::=
    term mulop factor <exp,0> |
    factor;

mulop ::= MUL | DIV | MOD;

factor ::=
    LP expression RP <factor,0> |
    variable |
    call |
    NUMBER;

call ::=
    ID LP RP <call,0> |
    ID LP arguments RP <call,0> ;

arguments ::=
    argument-list <args,0> ;

argument-list ::=
    argument-list COM expression <args-list,0> |
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