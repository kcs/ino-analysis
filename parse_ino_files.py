#!/usr/bin/env python3

import requests
import re
from datetime import datetime
import json


def get_ino_file(repo, ref, path):
    url = "https://raw.githubusercontent.com/" + repo + '/' + ref.split('/')[-1] + '/' + path
    print(f"{url}", end='')
    try:
        r = requests.get(url)
    except:
        print(f" failed. Ignoring")
        return None
    if r.status_code != 200:
        print(f" returned {r.status_code}. Ignoring")
        return None
    print(" OK")
    return r.text

keywords = {'auto', 'break', 'case', 'char', 'const', 'continue', 'default',
            'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto',
            'if', 'inline', 'int', 'long', 'register', 'return', 'short',
            'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef',
            'union', 'unsigned', 'void', 'volatile', 'while'}

class Parser:
    """ This is a parser object
    it creates some parsing rules, and then the parse function will go through the given code

    we parse for comments and strings to ignore it
    include directives
    anything that looks like a function call: [ any operator - not included ] string ( -also not included
    names followed by function call lookalikes are also ignored - probably definition
    not considering strange cases like comment between function name and paren
    """
    def __init__(self):
        self.result = None
        self.temp_name = None
        self.rules = {}
        for k in self.__dir__():
            if k.startswith('r_'):
                v = getattr(self, k)
                self.rules[k[2:]] = re.compile(v.__doc__, re.M)


    def parse_code(self, code):
        """ go through the code and identify the following:
            - included headers
            - anything that resembles a function call (except for keywords)
        """
        pos = 0
        length = len(code)
        self.temp_name = None
        self.result = {
            'includes': set(),
            'functions': {}
        }
        while pos < length:
            for k,v in self.rules.items():
                m = v.match(code, pos)
                if m:
                    t = getattr(self, 'r_' + k)(m)
                    if t is not None:
                        self.handle_token(k, t)
                    pos = m.end(0)
                    break
            else:
                # no tokens found, just ignore the first character
                pos += 1
                self.temp_name = None
        return self.result


    def handle_token(self, token, content):
        """ handle the token with the given content
            - include token is stored automatically into results
            - paren token will store the previous name token (if any)
            - name token will temporarily store it, waiting for a paren
            - sep token is used to concatenate names together for class members
        """
        if token == 'include':
            self.result['includes'].add(content)
        if token == 'paren':
            if self.temp_name:
                if self.temp_name in keywords:
                    pass
                elif self.temp_name in self.result['functions']:
                    self.result['functions'][self.temp_name] += 1
                else:
                    self.result['functions'][self.temp_name] = 1
        if token == 'sep' and self.temp_name:
            self.temp_name += '.'
        elif token == 'name':
            if self.temp_name:
                if self.temp_name[-1] == '.':
                    self.temp_name += content
                else:
                    self.temp_name = None
            else:
                self.temp_name = content
        else:
            self.temp_name = None


    # completely ignore whitespace and comments
    def r_whitespace(self, m):
        r'\s+'
        pass

    def r_comment(self, m):
        r'/\*(.|\n)*?\*/'
        pass

    def r_commentcpp(self, m):
        r'//.*\n'
        pass

    # include directive
    def r_include(self, m):
        r'#include\s+["<]([^>"]+)[">]'
        return m.group(1)

    # ignore any other preprocessor directives
    def r_pp(self, m):
        r'#(?!include)(.|\\\n)+\n'
        pass    

    # operators which can be followed by function call
    def r_op(self, m):
        r'[-+*/%|&~^!<>=;,?:)[{}]|<<|>>|\|\||&&|<=|>=|==|!=|\*=|/=|%=|\+=|-=|<<=|>>=|&=|\|=|^=|\+\+|--'
        return m.group(0)

    # operators which cannot be followed by function call
    def r_noop(self, m):
        r'[]]'
        return m.group(0)

    # opening paren
    def r_paren(self, m):
        r'\('
        return '('

    # separators in class/struct members
    def r_sep(self, m):
        r'\.|->'
        return '.'
    
    # string
    def r_string(self, m):
        r'\"([^\\\n]|(\\.))*?\"'
        return m.group(0)

    # character
    def r_char(self, m):
        r"(L)?\'([^\\\n]|(\\.))*?\'"
        return m.group(0)

    # integer
    def r_int(self, m):
        r'(0[xX])?\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'
        return m.group(0)

    # float
    def r_float(self, m):
        r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'
        return m.group(0)
 
    # names
    def r_name(self, m):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        return m.group(0)



parser = Parser()

if __name__ == "__main__":
    print(f"Script started at {datetime.now()}")

    with open("ino.json", "r") as f:
        json_rows = [json.loads(line) for line in f]

    try:
        with open("ino.done", "r") as f:
            done = int(f.read())
    except:
        done = 0

    for row in json_rows[done:]:
        # get the content
        print(done + 1, end=' ')
        x = get_ino_file(**row)

        if x:
            r = parser.parse_code(x)
            row['content'] = x
            row['includes'] = list(sorted(r['includes']))
            row['functions'] = r['functions']
            with open("ino_content.json", "a") as f:
                f.write(json.dumps(row, ensure_ascii=False, indent=None) + "\n")

        done += 1
        with open("ino.done", "w") as f:
            f.write(str(done))
    

    print(f"Script ended at {datetime.now()}")
