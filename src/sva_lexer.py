import ply.lex  as lex
from pathlib import Path

tokens = (
    # 通用关键字
    'LPAREN',       # (
    'RPAREN',       # )
    'LSQUARE',      # [
    'RSQUARE',      # ]
    'LBRACE',       # {
    'RBRACE',       # }
    'COLON',        # :
    'SEMICOLON',    # ;
    'COMMA',        # ,
    'BANG',         # !
    'POINT',        # .

    'NUMBER',       # 'd+'
    'PLUS',         # +
    'MINUS',        # -
    'STAR',         # *
    'DIVIDE',       # /
    'EQUALS',       # =
    'DOLLAR',       # $
    'GOTO',         # ->

    #序列关键字
    'SEQUENCE',     # sequence
    'ENDSEQUENCE',  # endsequence

    #序列内操作关键字  
    # 'SHARP',        # '#'
    'SHARP_SHARP',  # '##'

    #序列间操作关键字
    'AND',          # and
    'INTERSECT',    # intersect
    'OR',           # or
    'FIRST_MATCH',  # first_match
    'THROUGHOUT',   # throughout
    'WITHIN',       # within

    #属性关键字
    'PROPERTY',
    'ENDPROPERTY',

    'LOCAL'       ,
    'INPUT'       ,
    'OUTPUT'      ,
    'INOUT'       ,
    'UNTYPED'     ,
    'DISABLE'     ,
    'IFF'         ,
    'IF'          ,
    'ELSE'        ,
    'CASE'        ,
    'ENDCASE'     ,
    'DEFAULT'     ,

    'STRONG'                    ,
    'WEAK'                      ,
    'NOT'                       ,
    'OVERLAP_IMPLICATION'       ,
    'NON_OVERLAP_IMPLICATION'   ,
    'OVERLAP_FOLLOW_BY'         ,
    'NON_OVERLAP_FOLLOW_BY'     ,
    'NEXTTIME'                  ,
    'S_NEXTTIME'                ,
    'ALWAYS'                    ,
    'S_ALWAYS'                  ,
    'EVENTUALLY'                ,
    'S_EVENTUALLY'              ,
    'UNTIL'                     ,
    'S_UNTIL'                   ,
    'UNTIL_WITH'                ,
    'S_UNTIL_WITH'              ,
    'IMPLIES'                   ,
    'ACCEPT_ON'                 ,
    'REJECT_ON'                 ,
    'SYNC_ACCEPT_ON'            ,
    'SYNC_REJECT_ON'            ,

    # 断言关键字
    'ASSERT'                    ,
    'ASSUME'                    ,
    'COVER'                     ,
    'EXPECT'                    ,

    # 其他
    'DIST'                      ,
    'LET'                       ,
    'RESTRICT'                  ,

    'NAME',
    
)

t_LPAREN    =  r'\('
t_RPAREN    =  r'\)'
t_LSQUARE   =  r'\['
t_RSQUARE   =  r'\]'
t_LBRACE    =  r'\{'
t_RBRACE    =  r'\}'
t_COLON     =  r'\:'
t_SEMICOLON =  r'\;'
t_COMMA     =  r','
t_BANG      =  r'\!'
t_POINT     =  r'\.'

t_PLUS   = r'\+'
t_MINUS  = r'-'
t_STAR   = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'='
t_DOLLAR = r'\$'
t_GOTO   = r'->'

def t_SEQUENCE    (t):
    r'sequence'
    return t
def t_ENDSEQUENCE (t):
    r'endsequence'
    return t
# def t_SHARP       (t):
#    r'\#'
#    return t
def t_SHARP_SHARP (t):
    r'\#\#'
    return t
def t_AND         (t):
    r'and'
    return t
def t_INTERSECT   (t):
    r'intersect'
    return t
def t_OR          (t):
    r'or'
    return t
def t_FIRST_MATCH (t):
    r'first_match'
    return t
def t_THROUGHOUT  (t):
    r'throughout'
    return t
def t_WITHIN      (t):
    r'within'
    return t
def t_PROPERTY    (t):
    r'property'
    return t
def t_ENDPROPERTY (t):
    r'endproperty'
    return t

def t_LOCAL                   (t):
    r'local'
    return t
def t_INPUT                   (t):
    r'input'
    return t
def t_OUTPUT                  (t):
    r'output'
    return t
def t_INOUT                   (t):
    r'inout'
    return t
def t_UNTYPED                 (t):
    r'untyped'
    return t
def t_DISABLE                 (t):
    r'disable'
    return t
def t_IFF                     (t):
    r'iff'
    return t
def t_IF                      (t):
    r'if'
    return t
def t_ELSE                    (t):
    r'else'
    return t
def t_CASE                    (t):
    r'case'
    return t
def t_ENDCASE                 (t):
    r'endcase'
    return t
def t_DEFAULT                 (t):
    r'default'
    return t
def t_STRONG                  (t):
    r'strong'
    return t
def t_WEAK                    (t):
    r'weak'
    return t
def t_NOT                     (t):
    r'not'
    return t
def t_OVERLAP_IMPLICATION     (t):
    r'\|->'
    return t
def t_NON_OVERLAP_IMPLICATION (t):
    r'\|=>'
    return t
def t_OVERLAP_FOLLOW_BY       (t):
    r'\#-\#'
    return t
def t_NON_OVERLAP_FOLLOW_BY   (t):
    r'\#=\#'
    return t
def t_S_NEXTTIME              (t):
    r's_nexttime'
    return t
def t_NEXTTIME                (t):
    r'nexttime'
    return t
def t_S_ALWAYS                (t):
    r's_always'
    return t
def t_ALWAYS                  (t):
    r'always'
    return t
def t_S_EVENTUALLY            (t):
    r's_eventually'
    return t
def t_EVENTUALLY              (t):
    r'eventually'
    return t
def t_S_UNTIL_WITH            (t):
    r's_until_with'
    return t
def t_UNTIL_WITH            (t):
    r'until_with'
    return t
def t_S_UNTIL                 (t):
    r's_until'
    return t
def t_UNTIL                   (t):
    r'until'
    return t


def t_IMPLIES                 (t):
    r'implies'
    return t
def t_SYNC_ACCEPT_ON          (t):
    r'sync_accept_on'
    return t
def t_SYNC_REJECT_ON          (t):
    r'sync_reject_on'
    return t
def t_ACCEPT_ON               (t):
    r'accept_on'
    return t
def t_REJECT_ON               (t):
    r'reject_on'
    return t


# 断言关键字
def t_ASSERT            (t):
    r'assert'
    return t
def t_ASSUME            (t):
    r'assume'
    return t
def t_COVER             (t):
    r'cover'
    return t
def t_EXPECT            (t):
    r'expect'
    return t

# 其他
def t_DIST          (t):
    r'dist'
    return t
def t_LET           (t):
    r'let'
    return t
def t_RESTRICT      (t):
    r'restrict'
    return t


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def _should_rebuild_lextab(lextab_file: Path, source_files: list[Path]) -> bool:
    if not lextab_file.exists():
        return True
    try:
        lextab_mtime = lextab_file.stat().st_mtime
        latest_src_mtime = max(src.stat().st_mtime for src in source_files)
        return lextab_mtime < latest_src_mtime
    except FileNotFoundError:
        return True

_base_dir = Path(__file__).resolve().parent
_lextab_module = 'src.lextab_sva'
_lextab_path = _base_dir / 'lextab_sva.py'
_source_paths = [Path(__file__).resolve()]
_needs_rebuild = _should_rebuild_lextab(_lextab_path, _source_paths)

lexer = lex.lex(
    lextab=_lextab_module,
    optimize=not _needs_rebuild,
    outputdir=str(_base_dir),
    debug=_needs_rebuild
)