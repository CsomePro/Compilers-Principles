G[ program ];

program ::= definition-list <program,1> ;

definition-list ::=
    definition-list definition <def,2> |
    definition <program,1> ;

definition ::=
    variable-definition |
    function-definition;

variable-definition ::=
    type-indicator ID SEM <var,3> |
    type-indicator ID LSB NUMBER RSB SEM <var,6>;

type-indicator ::= INT | FLOAT | VOID;

function-definition ::= type-indicator ID LP parameters RP compound-stmt <func,6>;

parameters ::=
    parameter-list |
    VOID;

parameter-list ::=
    parameter-list COM  parameter <param-list,3> |
    parameter ;

parameter ::=
    type-indicator ID <param,2> |
    type-indicator ID LSB RSB <param,4>;

compound-stmt ::=
    OB  local-definitions statement-list  CB <compound,4> |
    OB  local-definitions  CB  <compound,3> |
    OB  statement-list CB <compound,3> |
    OB  CB <compound,2> ;

local-definitions ::= variable-definition local-definitions <local-list,2> | variable-definition  ;

statement-list ::= statement statement-list <stmt-list,2> |  statement ;

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
     IF  LP expression RP  statement <if,5> |
     IF  LP expression RP statement  ELSE  statement <if,7>;

dowhile-stmt ::=
    DO statement WHILE  LP  expression RP   SEM  <while,7>;

return-stmt ::=
    RETURN  SEM <return,2> |
    RETURN expression  SEM <return,3> ;

expression ::=
    variable ASSIGN expression  <exp,3> |
    simple-expression;

variable ::=
    ID |
    ID LSB expression RSB <var,4> ;

simple-expression ::=
    additive-expression relop additive-expression <exp,3> |
    additive-expression;

relop ::= LTE | LT | GT | GTE | EQ | NE;

additive-expression ::=
    additive-expression addop term <exp,3> |
    term;

addop ::= PLUS | MINUS;

term ::=
    term mulop factor <exp,3> |
    factor;

mulop ::= MUL | DIV | MOD;

factor ::=
    LP expression RP <factor,3> |
    variable |
    call |
    NUMBER;

call ::=
    ID LP RP <call,3> |
    ID LP arguments RP <call,4> ;

arguments ::=
    argument-list <args,1> ;

argument-list ::=
    argument-list COM expression <args-list,3> |
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