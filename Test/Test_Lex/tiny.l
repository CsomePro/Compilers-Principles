
// keyword
"[iI][fF]" IF
"[eE][lL][sS][eE]" ELSE
"[tT][hH][eE][nN]" THEN
"[eE][nN][dD]" END
"[rR][eE][pP][eE][aA][tT]" REPEAT
"[uU][nN][tT][iI][lL]" UNTIL
"[rR][eE][aA][dD]" READ
"[wW][rR][iI][tT][eE]" WRITE

// symbol
"\\+" PLUS
"-" MINUS
"\\*" MUL
"/" DIV
"<" LT
"=" EQ
";" SEM
":=" ASSIGN
"\\(" LP
"\\)" RP

// others
"[a-zA-Z][a-zA-Z]*" ID
"[0-9][0-9]*" NUMBER

// skip
"[ \t\n]+" skip
"{[ -z|~{\n]*}" skip
