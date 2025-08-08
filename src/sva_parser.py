import ply.yacc as yacc
from . import sva_lexer
from .sva_ast import *



debug_open = False

tokens = sva_lexer.tokens

precedence = (
    ('left', 'SHARP_SHARP', 'WITHIN','INTERSECT','AND','OR'),
    ('right','THROUGHOUT')
)

def p_start(p):
    '''
    start : sequence_declaration
            | property_declaration
        '''
    p[0] = p[1]

# 可选的冒号
# def p_optional_semicolon(p):
#     '''
#     optional_semicolon : 
#         | SEMICOLON
#     '''

# def p_optional_sequence_identifier(p):
#     '''
#     optional_sequence_identifier : 
#         | COLON NAME
#     '''


def p_sequence_declaration(p):
    '''
    sequence_declaration : SEQUENCE NAME SEMICOLON sequence_expr SEMICOLON ENDSEQUENCE
        '''
    p[0] = p[4]
    if debug_open  : 
        print(f"find sequence_declaration state = {p.parser.state} ")



# ---------------------------------- sequence_expr ----------------------------------
#| sequence_instance [ sequence_abbrev ] 
#| ( sequence_expr {, sequence_match_item } ) [ sequence_abbrev ] 
#| clocking_event sequence_expr
#| FIRST_MATCH LPAREN sequence_expr {, sequence_match_item} RPAREN                                      
# def p_sequence_expr(p):
#     '''sequence_expr : cycle_delay_range sequence_expr
#                      | sequence_expr cycle_delay_range sequence_expr 
#                      | expression_or_dist
#                      | expression_or_dist LSQUARE boolean_abbrev RSQUARE
#                      | sequence_expr AND sequence_expr 
#                      | sequence_expr INTERSECT sequence_expr 
#                      | sequence_expr OR sequence_expr 
#                      | FIRST_MATCH LPAREN sequence_expr RPAREN
#                      | expression_or_dist THROUGHOUT sequence_expr 
#                      | sequence_expr WITHIN sequence_expr 
#                      | LPAREN sequence_expr RPAREN
#     '''
#     if debug_open  : print(f"find sequence_expr state = {p.parser.state} ")

def p_sequence_expr0(p):
    '''sequence_expr : cycle_delay_range sequence_expr
    '''
    # p[0] = ['sequence_expr_delay_before_expr', p[1],['empty'], p[2]]
    ast_type = 'sequence_expr_delay_before_expr'
    op       = p[1]
    ast_empty = AstCreate(ast_type = 'empty')
    sub_asts = [ast_empty, p[2]]
    ast = AstCreate(ast_type , op ,sub_asts)
    p[0] = ast
    
    if debug_open  : 
        print(f"find sequence_expr0 state = {p.parser.state} ")

def p_sequence_expr_cycle_delay_range(p):
    '''sequence_expr : sequence_expr cycle_delay_range sequence_expr 
    '''
    # p[0] = ['sequence_expr', p[2], p[1],p[3]]
    ast_type = 'sequence_expr'
    op       = p[2]
    sub_asts = [p[1],p[3]]
    ast = AstCreate(ast_type , op ,sub_asts)
    p[0] = ast
    if debug_open  : 
        print(f"find sequence_expr1 state = {p.parser.state} ")

def p_sequence_expr1(p):
    '''sequence_expr : sequence_expr AND sequence_expr 
                    | sequence_expr INTERSECT sequence_expr 
                    | sequence_expr OR sequence_expr 
                    | expression_or_dist THROUGHOUT sequence_expr 
                    | sequence_expr WITHIN sequence_expr 
    '''
    # p[0] = ['sequence_expr', p[2], p[1],p[3]]
    ast_type = 'sequence_expr'
    op       = OperatorCreate(p[2],[0])
    sub_asts = [p[1],p[3]]
    ast = AstCreate(ast_type , op ,sub_asts)
    p[0] = ast
    if debug_open  : 
        print(f"find sequence_expr1 state = {p.parser.state} ")


def p_sequence_expr2(p):
    '''sequence_expr : expression_or_dist
    '''
    # p[0] = ['sequence_expr', ['constant_consecutive_repetition',[1]], p[1]]
    ast_type = 'sequence_expr'
    op       = OperatorCreate('constant_consecutive_repetition',[1])
    sub_asts = [p[1]]
    ast = AstCreate(ast_type , op ,sub_asts)
    p[0] = ast
    if debug_open  : 
        print(f"find sequence_expr2 state = {p.parser.state} ")

def p_sequence_expr3(p):
    '''sequence_expr : expression_or_dist boolean_abbrev 
    '''
    # p[0] = ['sequence_expr', p[2], p[1]]
    ast_type = 'sequence_expr'
    op       = p[2]
    sub_asts = [p[1]]
    ast = AstCreate(ast_type , op ,sub_asts)
    p[0] = ast
    if debug_open  : 
        print(f"find sequence_expr3 state = {p.parser.state} ")

def p_sequence_expr4(p):
    '''sequence_expr : FIRST_MATCH LPAREN sequence_expr RPAREN
    '''
    # p[0] = ['sequence_expr', p[1], p[3]]
    ast_type = 'sequence_expr'
    op       = OperatorCreate(p[1],[0])
    sub_asts = [p[3]]
    ast = AstCreate(ast_type , op ,sub_asts)
    p[0] = ast
    if debug_open  : 
        print(f"find sequence_expr4 state = {p.parser.state} ")

def p_sequence_expr5(p):
    '''sequence_expr : LPAREN sequence_expr RPAREN
    '''
    p[0] = p[2]
    if debug_open  : 
        print(f"find sequence_expr5 state = {p.parser.state} ")


#----------------------------------- cycle_delay_range ----------------------------------
#   constant_delay
#   range_delay
#   star_delay
#   plus_delay
def p_cycle_delay_range0(p) :
    ''' 
    cycle_delay_range : SHARP_SHARP constant_primary 
    '''
    # p[0] = ['constant_delay',p[2]]
    p[0] = OperatorCreate('constant_delay',p[2])
    if debug_open  : 
        print(f"find cycle_delay_range state = {p.parser.state} ")

def p_cycle_delay_range1(p) :
    ''' 
    cycle_delay_range : SHARP_SHARP LSQUARE cycle_delay_const_range_expression RSQUARE
    '''
    # p[0] = ['range_delay',p[3]]
    p[0] = OperatorCreate('range_delay',p[3])
    if debug_open  : 
        print(f"find cycle_delay_range state = {p.parser.state} ")


def p_cycle_delay_range2(p) :
    ''' 
    cycle_delay_range : SHARP_SHARP LSQUARE STAR RSQUARE
    '''
    # p[0] = ['star_delay',[0, '$']]
    p[0] = OperatorCreate('star_delay',[0, '$'])
    if debug_open  : 
        print(f"find cycle_delay_range state = {p.parser.state} ")

def p_cycle_delay_range3(p) :
    ''' 
    cycle_delay_range : SHARP_SHARP LSQUARE PLUS RSQUARE
    '''
    # p[0] = ['plus_delay',[1, '$']]
    p[0] = OperatorCreate('plus_delay',[0, '$'])
    if debug_open  : 
        print(f"find cycle_delay_range state = {p.parser.state} ")


#----------------------------------- boolean_abbrev -------------------------------
def p_boolean_abbrev(p):
    ''' 
    boolean_abbrev : consecutive_repetition 
        | non_consecutive_repetition
        | goto_repetition
    '''
    p[0] = p[1]
    if debug_open  : 
        print(f"find boolean_abbrev state = {p.parser.state} ")


#----------------------------------- consecutive_repetition -------------------------------
# constant_consecutive_repetition
# range_consecutive_repetition
# star_consecutive_repetition
# plus_consecutive_repetition
def p_consecutive_repetition0(p):
    ''' 
    consecutive_repetition : LSQUARE STAR const_or_range_expression RSQUARE
    '''
    if len(p[3]) == 1 :
        # p[0] = ['constant_consecutive_repetition', p[3]]
        p[0] = OperatorCreate('constant_consecutive_repetition',p[3])
    else:
        # p[0] = ['range_consecutive_repetition', p[3]]
        p[0] = OperatorCreate('range_consecutive_repetition',p[3])
    if debug_open  : 
        print(f"find consecutive_repetition state = {p.parser.state} ")



def p_consecutive_repetition1(p):
    ''' 
    consecutive_repetition : LSQUARE STAR RSQUARE
    '''
    # p[0] = ['star_consecutive_repetition', [0, '$']]
    p[0] = OperatorCreate('star_consecutive_repetition',[0, '$'])
    if debug_open  : 
        print(f"find consecutive_repetition state = {p.parser.state} ")

def p_consecutive_repetition2(p):
    ''' 
    consecutive_repetition : LSQUARE PLUS RSQUARE
    '''
    # p[0] = ['plus_consecutive_repetition', [1, '$']]
    p[0] = OperatorCreate('plus_consecutive_repetition',[0, '$'])
    if debug_open  : 
        print(f"find consecutive_repetition state = {p.parser.state} ")


#----------------------------------- non_consecutive_repetition -------------------------------
# constant_non_consecutive_repetition
# range_non_consecutive_repetition
def p_non_consecutive_repetition(p):
    ''' 
    non_consecutive_repetition : LSQUARE EQUALS const_or_range_expression RSQUARE
    '''
    if len(p[3]) == 1 :
        # p[0] = ['constant_non_consecutive_repetition', p[3]]
        p[0] = OperatorCreate('constant_non_consecutive_repetition',p[3])
    else:
        # p[0] = ['range_non_consecutive_repetition', p[3]]
        p[0] = OperatorCreate('range_non_consecutive_repetition',p[3])
    if debug_open  : 
        print(f"find non_consecutive_repetition state = {p.parser.state} ")


#----------------------------------- goto_repetition -------------------------------
# constant_goto_repetition
# range_goto_repetition
def p_goto_repetition(p):
    ''' 
    goto_repetition : LSQUARE GOTO const_or_range_expression RSQUARE
    '''
    if len(p[3]) == 1 :
        # p[0] = ['constant_goto_repetition', p[3]]
        p[0] = OperatorCreate('constant_goto_repetition',p[3])
    else:
        # p[0] = ['range_goto_repetition', p[3]]
        p[0] = OperatorCreate('range_goto_repetition',p[3])
    if debug_open  : 
        print(f"find non_consecutive_repetition state = {p.parser.state} ")

#----------------------------------- const_or_range_expression -------------------------------
def p_const_or_range_expression(p):
    ''' 
    const_or_range_expression : constant_expression 
        | cycle_delay_const_range_expression
    ''' 
    p[0] = p[1]
    if debug_open  : 
        print(f"find const_or_range_expression state = {p.parser.state} ")







# ------------------------------- cycle_delay_const_range_expression ------------------------
def p_cycle_delay_const_range_expression0(p):
    '''
    cycle_delay_const_range_expression : constant_expression COLON constant_expression
    '''
    p[0] = p[1]
    p[0][1:] = p[3]
    if debug_open  : 
        print(f"find cycle_delay_const_range_expression state = {p.parser.state} ")
def p_cycle_delay_const_range_expression1(p):
    '''
    cycle_delay_const_range_expression : constant_expression COLON DOLLAR
    '''
    p[0] = p[1]
    p[0][1:] = '$'
    if debug_open  : 
        print(f"find cycle_delay_const_range_expression state = {p.parser.state} ")


# --------------------------------- constant_expression -----------------------
def p_constant_expression(p):
    ''' 
    constant_expression : NUMBER
    '''
    p[0] = [p[1]]
    if debug_open  : 
        print(f"find constant_expression state = {p.parser.state} ")



# ------------------------------- constant_primary ------------------------
#FIXME
def p_constant_primary(p) :
    ''' 
    constant_primary : NUMBER
    '''
    p[0] = [p[1]]
    if debug_open  : 
        print(f"find constant_primary state = {p.parser.state} ")


# ------------------------------- expression_or_dist ------------------------
#FIXME expression [ dist { dist_list } ]
def p_expression_or_dist(p) :
    '''
    expression_or_dist : expression
    '''
    # p[0] = ['expression_or_dist',[None,[0]],p[1]]
    ast_type = 'expression_or_dist'
    op       = None
    sub_asts = [p[1]]
    ast = AstCreate(ast_type , op ,sub_asts)
    p[0] = ast
    if debug_open  : 
        print(f"find expression_or_dist state = {p.parser.state}")


# ------------------------------- expression ------------------------
#FIXME 暂时就用变量名字
def p_expression0(p) :
    '''
    expression : NAME 
    '''
    # p[0] = [p[1]]
    ast_type = 'expression'
    op       = None
    sub_asts = []
    name = p[1]
    ast  = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast
    if debug_open  : 
        print(0)

def p_expression1(p) :
    '''
    expression : BANG NAME
    '''
    # p[0] = [f'!{p[2]}']
    ast_type = 'expression'
    op       = None
    sub_asts = []
    name = f'!{p[2]}'
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast
    if debug_open  : 
        print(1)

# ------------------------------- property_declaration ------------------------
# property_declaration ::= 
# property property_identifier [ ( [ property_port_list ] ) ] ;
# { assertion_variable_declaration } 
#  property_spec [ ; ] 
# endproperty [ : property_identifier ]
#FIXME 暂时只做
# property_declaration ::= 
# property property_identifier ;
#  property_spec [ ; ] 
# endproperty [ : property_identifier ]

# def p_optional_property_identifier(p):
#     '''
#     optional_property_identifier : 
#         | COLON NAME
#     '''

#FIXME 暂时不做端口变量
# def p_property_port_list()

#FIXME 暂时不做局部变量
def p_property_declaration(p):
    '''
    property_declaration : PROPERTY property_identifier SEMICOLON property_spec SEMICOLON ENDPROPERTY
    '''
    p[0] = p[4]

def p_property_identifier(p):
    '''
    property_identifier : NAME
    '''


# ------------------------------- property_spec ------------------------
# property_spec ::= 
# [clocking_event ] [ disable iff ( expression_or_dist ) ] property_expr
#FIXME 暂时只做
# property_spec ::= 
#   property_expr

def p_property_spec(p):
    '''
    property_spec : property_expr
    '''
    p[0] = p[1]




# ------------------------------- property_expr ------------------------
# property_expr ::= 
# sequence_expr
# | strong ( sequence_expr )
# | weak ( sequence_expr )
# | ( property_expr )
# | not property_expr 
# | property_expr or property_expr 
# | property_expr and property_expr 
# | sequence_expr |-> property_expr 
# | sequence_expr |=> property_expr 
# | if ( expression_or_dist ) property_expr [ else property_expr ] 
# | case ( expression_or_dist ) property_case_item { property_case_item } endcase
# | sequence_expr #-# property_expr 
# | sequence_expr #=# property_expr 
# | nexttime property_expr 
# | nexttime [ constant _expression ] property_expr 
# | s_nexttime property_expr 
# | s_nexttime [ constant_expression ] property_expr 
# | always property_expr 
# | always [ cycle_delay_const_range_expression ] property_expr 
# | s_always [ constant_range] property_expr 
# | s_eventually property_expr 
# | eventually [ constant_range ] property_expr 
# | s_eventually [ cycle_delay_const_range_expression ] property_expr 
# | property_expr until property_expr 
# | property_expr s_until property_expr 
# | property_expr until_with property_expr 
# | property_expr s_until_with property_expr 
# | property_expr implies property_expr 
# | property_expr iff property_expr
# | accept_on ( expression_or_dist ) property_expr 
# | reject_on ( expression_or_dist ) property_expr 
# | sync_accept_on ( expression_or_dist ) property_expr 
# | sync_reject_on ( expression_or_dist ) property_expr 
# | property_instance 
# | clocking_event property_expr

def p_property_expr_paren(p):
    '''
    property_expr : LPAREN property_expr RPAREN
    '''
    p[0] = p[2]

# sequence_expr
def p_property_expr0(p):
    '''
    property_expr : sequence_expr
    '''
    p[0] = p[1]

# strong ( sequence_expr )
def p_property_expr1(p):
    '''
    property_expr : STRONG LPAREN sequence_expr RPAREN
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('strong',[0])
    sub_asts = [p[3]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# weak ( sequence_expr )
def p_property_expr2(p):
    '''
    property_expr : WEAK LPAREN sequence_expr RPAREN
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('weak',[0])
    sub_asts = [p[3]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# not property_expr
def p_property_expr3(p):
    '''
    property_expr : NOT sequence_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('not',[0])
    sub_asts = [p[2]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# property_expr or property_expr
def p_property_expr4(p):
    '''
    property_expr : property_expr OR property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('or',[0])
    sub_asts = [p[1],p[3]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# property_expr and property_expr
def p_property_expr5(p):
    '''
    property_expr : property_expr AND property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('and',[0])
    sub_asts = [p[1],p[3]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

#  sequence_expr |-> property_expr
def p_property_expr6(p):
    '''
    property_expr : sequence_expr OVERLAP_IMPLICATION property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('overlap_implication',[0])
    sub_asts = [p[1],p[3]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

#  sequence_expr |=> property_expr
def p_property_expr7(p):
    '''
    property_expr : sequence_expr NON_OVERLAP_IMPLICATION property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('non_overlap_implication',[0])
    sub_asts = [p[1],p[3]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

#FIXME
# if ( expression_or_dist ) property_expr [ else property_expr ]

#FIXME 
# case ( expression_or_dist ) property_case_item { property_case_item } endcase




# sequence_expr #-# property_expr
def p_property_expr8(p):
    '''
    property_expr : sequence_expr OVERLAP_FOLLOW_BY property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('overlap_follow_by',[0])
    sub_asts = [p[1],p[3]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# sequence_expr #=# property_expr
def p_property_expr9(p):
    '''
    property_expr : sequence_expr NON_OVERLAP_FOLLOW_BY property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('non_overlap_follow_by',[0])
    sub_asts = [p[1],p[3]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# nexttime property_expr
def p_property_expr10(p):
    '''
    property_expr : NEXTTIME property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('nexttime',[0])
    sub_asts = [p[2]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# nexttime [ constant _expression ] property_expr
def p_property_expr11(p):
    '''
    property_expr : NEXTTIME LSQUARE constant_expression RSQUARE property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('nexttime',p[3])
    sub_asts = [p[5]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# s_nexttime property_expr
def p_property_expr12(p):
    '''
    property_expr : S_NEXTTIME property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('s_nexttime',[0])
    sub_asts = [p[2]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# s_nexttime [ constant_expression ] property_expr
def p_property_expr13(p):
    '''
    property_expr : S_NEXTTIME LSQUARE constant_expression RSQUARE property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('s_nexttime',p[3])
    sub_asts = [p[5]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# always property_expr
def p_property_expr14(p):
    '''
    property_expr : ALWAYS property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('always',[0])
    sub_asts = [p[2]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# always [ cycle_delay_const_range_expression ] property_expr
def p_property_expr15(p):
    '''
    property_expr : ALWAYS LSQUARE cycle_delay_const_range_expression RSQUARE property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('always',p[3])
    sub_asts = [p[5]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# s_always [ constant_range] property_expr
def p_property_expr16(p):
    '''
    property_expr : S_ALWAYS LSQUARE constant_range RSQUARE property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('s_always',p[3])
    sub_asts = [p[5]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# eventually [ constant_range ] property_expr
def p_property_expr17(p):
    '''
    property_expr : EVENTUALLY LSQUARE constant_range RSQUARE property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('eventually',p[3])
    sub_asts = [p[5]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# s_eventually property_expr
def p_property_expr18(p):
    '''
    property_expr : S_EVENTUALLY property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('s_eventually',[0])
    sub_asts = [p[2]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# s_eventually [ cycle_delay_const_range_expression ] property_expr
def p_property_expr19(p):
    '''
    property_expr : S_EVENTUALLY LSQUARE cycle_delay_const_range_expression RSQUARE property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('s_eventually',p[3])
    sub_asts = [p[5]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# property_expr until property_expr
def p_property_expr20(p):
    '''
    property_expr : property_expr UNTIL property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('until',[0])
    sub_asts = [p[1],p[3]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# property_expr s_until property_expr
def p_property_expr21(p):
    '''
    property_expr : property_expr S_UNTIL property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('s_until',[0])
    sub_asts = [p[1],p[3]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# property_expr until_with property_expr
def p_property_expr22(p):
    '''
    property_expr : property_expr UNTIL_WITH property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('until_with',[0])
    sub_asts = [p[1],p[3]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# property_expr s_until_with property_expr
def p_property_expr23(p):
    '''
    property_expr : property_expr S_UNTIL_WITH property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('s_until_with',p[3])
    sub_asts = [p[1],p[3]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# property_expr implies property_expr
def p_property_expr24(p):
    '''
    property_expr : property_expr IMPLIES property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('implies',p[3])
    sub_asts = [p[1],p[3]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# property_expr iff property_expr
def p_property_expr25(p):
    '''
    property_expr : property_expr IFF property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('iff',p[3])
    sub_asts = [p[1],p[3]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# accept_on ( expression_or_dist ) property_expr
def p_property_expr26(p):
    '''
    property_expr : ACCEPT_ON LPAREN expression_or_dist RPAREN property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('accept_on',p[3])
    sub_asts = [p[5]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# reject_on ( expression_or_dist ) property_expr
def p_property_expr27(p):
    '''
    property_expr : REJECT_ON LPAREN expression_or_dist RPAREN property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('reject_on',p[3])
    sub_asts = [p[5]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# sync_accept_on ( expression_or_dist ) property_expr
def p_property_expr28(p):
    '''
    property_expr : SYNC_ACCEPT_ON LPAREN expression_or_dist RPAREN property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('sync_accept_on',p[3])
    sub_asts = [p[5]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast

# sync_reject_on ( expression_or_dist ) property_expr
def p_property_expr29(p):
    '''
    property_expr : SYNC_REJECT_ON LPAREN expression_or_dist RPAREN property_expr
    '''
    ast_type = 'property_expr'
    op       = OperatorCreate('sync_reject_on',p[3])
    sub_asts = [p[5]]
    name = f''
    ast = AstCreate(ast_type , op ,sub_asts, name)
    p[0] = ast


#FIXME
# | property_instance 

#FIXME
# | clocking_event property_expr


















def p_constant_range(p):
    '''
    constant_range : constant_expression COLON constant_expression
    '''
    p[0] = p[1] + p[3]




# def p_expression_plus(p):
#     'expression : \
#      expression PLUS term'
#     p[0] = p[1] + p[3]

# def p_expression_minus(p):
#     'expression : expression MINUS term'
#     p[0] = p[1] - p[3]

# def p_expression_term(p):
#     'expression : term'
#     p[0] = p[1]

# def p_term_times(p):
#     'term : term STAR factor'
#     p[0] = p[1] * p[3]

# def p_term_div(p):
#     'term : term DIVIDE factor'
#     p[0] = p[1] / p[3]

# def p_term_factor(p):
#     'term : factor'
#     p[0] = p[1]

# def p_factor_num(p):
#     'factor : NUMBER'
#     p[0] = p[1]

# def p_factor_expr(p):
#     'factor : LPAREN expression RPAREN'
#     p[0] = p[2]

# Error rule for syntax errors
def p_error(p):
    """语法解析错误"""
    print(f'Syntax error in input! state = {parser.state}')
    print(p)

# Build the parser
parser = yacc.yacc(debug=True)
