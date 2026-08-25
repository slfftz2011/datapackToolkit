import re
from constants import COLOR_MAP, STYLE_MAP

def strip_json_keys(json_str: str) -> str:
    """移除 JSON 键名的双引号"""
    pattern = r'"([a-zA-Z_][a-zA-Z0-9_]*)":'
    return re.sub(pattern, r'\1:', json_str)

def parse_line(line: str) -> list[dict]:
    """
    解析一行富文本，返回 JSON 组件列表。
    支持 & 格式码、\n 换行（实际已拆分）、&w...&w...&p 链接，
    以及转义 \&、\\、\b。
    """
    components = []
    text_buf = ''
    style = {}
    link_state = 0          # 0=普通, 1=链接显示文本, 2=链接路径
    link_display = ''
    link_path = ''

    i = 0
    n = len(line)

    def flush_text():
        nonlocal text_buf
        if text_buf:
            comp = {'text': text_buf}
            comp.update(style)
            components.append(comp)
            text_buf = ''

    def finish_link():
        nonlocal link_state, link_display, link_path
        if link_state == 0:
            return
        display_comps = parse_line(link_display) if link_display else [{'text': ''}]
        if link_path.startswith(('http://', 'https://')):
            action = 'open_url'
            value = link_path
        else:
            action = 'run_command'
            if not link_path.startswith('/'):
                link_path = '/function age:gamerule/' + link_path
            value = link_path
        for comp in display_comps:
            comp['click_event'] = {'action': action, 'value': value}
        components.extend(display_comps)
        link_state = 0
        link_display = ''
        link_path = ''

    while i < n:
        ch = line[i]

        # 处理转义
        if ch == '\\' and i + 1 < n:
            nxt = line[i+1]
            if nxt == '&':
                target = text_buf if link_state == 0 else (link_display if link_state == 1 else link_path)
                target += '&'
                i += 2
                continue
            elif nxt == '\\':
                target = text_buf if link_state == 0 else (link_display if link_state == 1 else link_path)
                target += '\\'
                i += 2
                continue
            elif nxt == 'b':
                target = text_buf if link_state == 0 else (link_display if link_state == 1 else link_path)
                target += '  '
                i += 2
                continue
            else:
                # 其他转义保留原样
                target = text_buf if link_state == 0 else (link_display if link_state == 1 else link_path)
                target += '\\' + nxt
                i += 2
                continue
        elif ch == '\\' and i + 1 == n:
            # 行末单独反斜杠
            target = text_buf if link_state == 0 else (link_display if link_state == 1 else link_path)
            target += '\\'
            i += 1
            continue

        # 处理格式码
        if ch == '&' and i + 1 < n:
            code = line[i+1]
            if code == 'r':
                i += 2
                continue
            elif code == 'w':
                if link_state == 0:
                    flush_text()
                    link_state = 1
                    link_display = ''
                elif link_state == 1:
                    link_state = 2
                    link_path = ''
                elif link_state == 2:
                    finish_link()
                    link_state = 1
                    link_display = ''
                i += 2
                continue
            elif code == 'p':
                if link_state != 0:
                    finish_link()
                i += 2
                continue
            else:
                flush_text()
                if code in COLOR_MAP:
                    style['color'] = COLOR_MAP[code]
                elif code in STYLE_MAP:
                    style[STYLE_MAP[code]] = True
                i += 2
                continue

        # 普通字符
        if link_state == 0:
            text_buf += ch
        elif link_state == 1:
            link_display += ch
        else:
            link_path += ch
        i += 1

    flush_text()
    if link_state != 0:
        finish_link()
    return components