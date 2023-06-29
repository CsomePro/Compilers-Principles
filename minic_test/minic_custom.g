G[ program ];

program ::= definition-list <program,0> ;

definition-list ::=
    definition-list definition <definition,0> |
    definition ;

definition ::=
    variable-definition |
    function-definition;

variable-definition ::=
    type-indicator ID SEM <var_3,0> |
    type-indicator ID LSB NUMBER RSB SEM <var_6,0>;

type-indicator ::= INT | FLOAT | VOID;

function-definition ::= type-indicator ID LP parameters RP compound-stmt <func_def,0>;

parameters ::=
    parameter-list |
    VOID;

parameter-list ::=
    parameter-list COM  parameter <param_list,0> |
    parameter ;

parameter ::=
    type-indicator ID <param_id,0> |
    type-indicator ID LSB RSB <param_array,0>;

compound-stmt ::=
    OB  local-definitions statement-list  CB <compound_4,0> |
    OB  local-definitions  CB  <compound_3,0> |
    OB  statement-list CB <compound_2,0> |
    OB  CB <compound_1,0> ;

local-definitions ::= local-definitions variable-definition <local_list,0> | variable-definition  ;

statement-list ::= statement-list statement <stmt_list,0> |  statement ;

statement ::=
    expression-stmt |
    compound-stmt |
    condition-stmt |
    dowhile-stmt |
    return-stmt;

expression-stmt ::=
    expression  SEM <exp_sem,0> |
    SEM <exp_empty,0>;

condition-stmt ::=
     IF  LP expression RP  statement <if_stmt,0> |
     IF  LP expression RP statement  ELSE  statement <if_else,0>;

dowhile-stmt ::=
    DO statement WHILE  LP  expression RP   SEM  <while_stmt,0>;

return-stmt ::=
    RETURN  SEM <return_void,0> |
    RETURN expression  SEM <return_exp,0> ;

expression ::=
    ID ASSIGN expression <exp_assign_id,0> |
    ID LSB expression RSB ASSIGN expression <exp_assign_array,0> |
    simple-expression;

variable ::=
    ID <var_id,0> |
    ID LSB expression RSB <var_array,0> ;

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
    NUMBER <factor_const,0>;

call ::=
    ID LP RP <call_non_arg,0> |
    ID LP arguments RP <call_args,0> ;

arguments ::=
    argument-list ;

argument-list ::=
    argument-list COM expression <args_list,0> |
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