import re

MULTIPLIER = 0   # syntax: [number, thing_to_repeat]
INTERVAL = 1     # syntax: [time_in_seconds, ftp_fraction_as_float]
COOLDOWN_WARMUP = 2    # syntax: [time_in_seconds, ftp_fraction_start, ftp_fraction_end]

re_single_interval = re.compile(r'^\s*([0-9]{1,4}(?:\s*[sSmM][a-zA-Z]*?|:[0-9]{1,2}))[^a-zA-Z0-9]+([0-9]{1,3}\s*%?|[0-9]\.[0-9]*)\s*$')
re_cooldown_warmup = re.compile(r'^\s*([0-9]{1,4}(?:\s*[sSmM][a-zA-Z]*?|:[0-9]{1,2}))[^a-zA-Z0-9]+([0-9]{1,3}\s*%?|[0-9]\.[0-9]*)\s*-+>*\s*([0-9]{1,3}\s*%?|[0-9]\.[0-9]*)\s*$')
re_mult = re.compile(r'^\s*([1-9])\s*[xX*]\s*$')

# LINES = '10 minuten 40 -80%\n 1 Minute 110% \n 3 Minuten 60 % \n3x {\n3x { 10 Sekunden 200%\n 1:50 100%\n 2 Minuten 40%}\n 7 Minuten 40%}\n5 Minuten 40-20%'.splitlines()
LINES = '10 minuten 40 -80%\n 1 Minute 110% \n 3 Minuten 60 % \n3x (\n3x ( 3 Minuten 100%\n 3 Minuten 80% )\n 5 Minuten 40%)\n5 Minuten 40-20%'.splitlines()


def parse_wattage_string(s):
    if '%' in s:
        s = s.split('%')[0].strip()
    if not s.replace('.', '').isnumeric():
        print("Unexpected error. Wattage is not numeric: {}".format(s))
        return 0
    numb = float(s)
    if '.' in s:
        return numb
    else:
        return numb / 100


def parse_time_string(s):
    if ':' in s:
        spl = s.split(':')
        min_str = spl[0]
        sec_str = spl[1]
        if not min_str.isnumeric() or not sec_str.isnumeric():
            print("Unexpected error. Minutes or seconds are not numeric: {}".format(s))
            return 0
        seconds = int(min_str)*60 + int(sec_str)
    else:
        re_time = re.compile(r'([0-9]{1,4})\s*([sSmM][a-zA-Z]*)?')
        m = re_time.match(s)
        tim = m.group(1)
        if not tim.isnumeric():
            print("Unexpected error. Minutes or seconds are not numeric: {}".format(s))
            return 0
        try:
            unit = m.group(2)
        except IndexError:
            unit = ''
        if unit.lower().startswith('m'):
            seconds = int(tim)*60
        elif unit.lower().startswith('s'):
            seconds = int(tim)
        else:
            print("Unexpected error. Time unit does not begin with s or m: {}".format(s))
            return 0
    return seconds


def parse_interval_line(l_interval):

    if len(l_interval) > 0 and not l_interval.isspace():
        m = re_single_interval.match(l_interval)
        if m is None:
            m = re_cooldown_warmup.match(l_interval)
            if m is None:
                raise SyntaxError

            # here we have a cooldown warmup match
            time_string = m.group(1).strip()
            wattage_string1 = m.group(2).strip()
            wattage_string2 = m.group(3).strip()

            seconds = parse_time_string(time_string)
            wattage1 = parse_wattage_string(wattage_string1)
            wattage2 = parse_wattage_string(wattage_string2)

            return [COOLDOWN_WARMUP, seconds, wattage1, wattage2]

        # here we have a single interval match
        time_string = m.group(1).strip()
        wattage_string = m.group(2).strip()

        seconds = parse_time_string(time_string)
        wattage = parse_wattage_string(wattage_string)

        return [INTERVAL, seconds, wattage]

    return None


def parse_repetition_line(l_mult):
    if len(l_mult) > 0 and not l_mult.isspace():
        m = re_mult.match(l_mult)
        if m is None:
            raise SyntaxError
        mult_str = m.group(1)
        return int(mult_str)

    return 1


def parse_lines(lines):

    def update_append_to(base, num):
        indexing_string = ''
        for j in range(num):
            indexing_string += '[-1][-1]'
        append_to = eval('base' + indexing_string)
        return append_to

    parsed_string = []
    open_muls = 0
    append_to = parsed_string
    for li, l in enumerate(lines):
        split_at = '{'
        for s in '{([':
            if s in l:
                split_at = s
                break
        lopen = l.split(split_at)
        if len(lopen) == 1:
            split_at = '}'
            for s in '})]':
                if s in l:
                    split_at = s
                    break
            lclose = l.split(split_at)
            l_interval = lclose[0]
            try:
                interv = parse_interval_line(l_interval)
            except SyntaxError:
                raise SyntaxError('Syntax error: Failed to parse interval string.', ("user entry", li, 0, l_interval))
                # print("Syntax error in line {}: {}".format(li, l_interval))
                # break
            if interv is not None:
                append_to.append(interv)
            if '}' in l or ')' in l or ']' in l:
                open_muls -= 1
                append_to = update_append_to(parsed_string, open_muls)
        else:
            l_mult = lopen[0]
            l_interval = lopen[1]
            try:
                mult = parse_repetition_line(l_mult)
            except SyntaxError:
                raise SyntaxError('Syntax error: Failed to parse repetition string.', ("user entry", li, 0, l_mult))
                # print("Syntax error in line {}: {}".format(li, l_mult))
                # break
            try:
                interv = parse_interval_line(l_interval)
            except SyntaxError:
                raise SyntaxError('Syntax error: Failed to parse interval string.', ("user entry", li, 0, l_interval))
                # print("Syntax error in line {}: {}".format(li, l_interval))
                # break

            if mult > 1:
                append_to.append([MULTIPLIER, mult, []])
                open_muls += 1
                append_to = update_append_to(parsed_string, open_muls)

            if interv is not None:
                append_to.append(interv)

    return parsed_string


if __name__ == '__main__':
    parsed_string = parse_lines(LINES)
    print(parsed_string)
