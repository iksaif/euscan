import re
import cgi

colorcodes = {
    'bold': ('\033[1m', '\033[22m'),
    'cyan': ('\033[36m', '\033[39m'),
    'blue': ('\033[34m', '\033[39m'),
    'red': ('\033[31m', '\033[39m'),
    'magenta': ('\033[35m', '\033[39m'),
    'green': ('\033[32m', '\033[39m'),
    'underline': ('\033[4m', '\033[24m'),
}


def recolor(color, text):
    regexp = "(?:%s)(.*?)(?:%s)" % colorcodes[color]
    regexp = regexp.replace('[', r'\[')
    return re.sub(
        regexp, r'''<span style="color: %s">\1</span>''' % color, text
    )


def bold(text):
    regexp = "(?:%s)(.*?)(?:%s)" % colorcodes['bold']
    regexp = regexp.replace('[', r'\[')
    return re.sub(regexp, r'<span style="font-weight:bold">\1</span>', text)


def underline(text):
    regexp = "(?:%s)(.*?)(?:%s)" % colorcodes['underline']
    regexp = regexp.replace('[', r'\[')
    return re.sub(
        regexp, r'<span style="text-decoration: underline">\1</span>', text
    )


def removebells(text):
    return text.replace('\07', '')


def removebackspaces(text):
    backspace_or_eol = r'(.\010)|(\033\[K)'
    n = 1
    while n > 0:
        text, n = re.subn(backspace_or_eol, '', text, 1)
    return text


def plaintext2html(text, tabstop=4):
    def do_sub(m):
        c = m.groupdict()
        if c['htmlchars']:
            return cgi.escape(c['htmlchars'])
        if c['lineend']:
            return '<br>'
        elif c['space']:
            t = m.group().replace('\t', '&nbsp;' * tabstop)
            t = t.replace(' ', '&nbsp;')
            return t
        elif c['space'] == '\t':
            return ' ' * tabstop
        else:
            url = m.group('protocal')
            if url.startswith(' '):
                prefix = ' '
                url = url[1:]
            else:
                prefix = ''
            last = m.groups()[-1]
            if last in ['\n', '\r', '\r\n']:
                last = '<br>'
            return '%s%s' % (prefix, url)
    re_string = re.compile(
        r'(?P<htmlchars>[<&>])|(?P<space>^[ \t]+)|(?P<lineend>\r\n|\r|\n)|'
        r'(?P<protocal>(^|\s)((http|ftp)://.*?))(\s|$)',
        re.S | re.M | re.I
    )
    result = re.sub(re_string, do_sub, text)
    result = recolor('cyan', result)
    result = recolor('blue', result)
    result = recolor('red', result)
    result = recolor('magenta', result)
    result = recolor('green', result)
    result = bold(result)
    result = underline(result)
    result = removebells(result)
    result = removebackspaces(result)

    return result
