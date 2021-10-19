abb = {'руб.': 'руб',
       'шт.': 'шт'}


def kill_space(text_space):
    if len(text_space) != 0:
        text_space = text_space.replace('          ', ' ')
        text_space = text_space.replace('         ', ' ')
        text_space = text_space.replace('        ', ' ')
        text_space = text_space.replace('       ', ' ')
        text_space = text_space.replace('      ', ' ')
        text_space = text_space.replace('     ', ' ')
        text_space = text_space.replace('    ', ' ')
        text_space = text_space.replace('   ', ' ')
        text_space = text_space.replace('   ', ' ')
        text_space = text_space.replace('  ', ' ')

        if text_space[0] == ' ':
            text_space = text_space[1:]

        if len(text_space) != 0:
            if text_space[-1] == ' ':
                text_space = text_space[:-1]
        else:
            return -1

        return text_space

    else:
        return -1


def clear_inclusiv(l_in):
    l_out = []

    if len(l_in) > 1:
        for i in range(len(l_in)):
            flag = 0
            for j in range(len(l_in)):
                if (l_in[i] in l_in[j]):
                    flag += 1
            if flag == 1:
                l_out.append(l_in[i])

    elif len(l_in) == 1:
        l_out.append(l_in[0])

    return l_out


def del_double(text):
    '''
    :Вход: анализируемая строка (string)


    :Выход: строку без дублей и список из строк (предложений)
            Если на вход была получена нулевая строка - вернёт в качестве списка "-1" и "-1"
            в качестве строки.
    '''

    if len(text) != 0:
        no_abb = text.replace('...', '.')
        no_abb = no_abb.replace('<br>', ' . ')
        no_abb = kill_space(no_abb)

        for t in abb:
            no_abb = no_abb.replace(t, abb[t])
            for i in range(len(no_abb)):
                if no_abb[i:i + len(abb[t])] == abb[t]:
                    if i + len(abb[t]) < len(no_abb):
                        if (no_abb[i + len(abb[t])] == ' ' and no_abb[i + len(abb[t]) + 1].isupper()) or (
                                no_abb[i + len(abb[t])].isupper()):
                            no_abb = no_abb[:i + len(abb[t])] + '.' + no_abb[i + len(abb[t]):]

        no_abb = no_abb.split('.')
        for n, str_ in enumerate(no_abb):
            no_abb[n] = kill_space(str_)

        out_list = []
        for line in no_abb:
            if line not in out_list:
                if line != -1:
                    out_list.append(line)

        out_list = clear_inclusiv(out_list)

        out_string = '. '.join(out_list)
        out_string += '.'

        return out_string, out_list

    else:
        return -1, -1


string_ ,list_ = del_double(t1)