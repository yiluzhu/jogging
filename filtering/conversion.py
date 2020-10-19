import datetime


def make_lv1_filters(filter_str):
    if filter_str.startswith('(') and filter_str.endswith(')'):
        filter_str = filter_str[1:-1]
    field, op, value = [x for x in filter_str.split(' ') if x]

    value = eval(value)
    if isinstance(value, str):
        try:
            value = datetime.datetime.strptime(value, '%Y-%m-%d').date()
        except Exception:
            pass
    return {
        'field': field,
        'op': op,
        'value': value,
    }


def make_lv2_filters(filter_list):
    if isinstance(filter_list, list):
        return {
            filter_list[1].lower(): [
                make_lv2_filters(filter_list[0]),
                make_lv2_filters(filter_list[2])
            ]
        }
    else:
        return make_lv1_filters(filter_list)


def convert_str_to_filters(filter_str):
    """Given a filter string, return corresponding filter dict

    :param filter_str: a string representation of filters, e.g. "(username == 'john') and ((distance > 2500) or (distance < 1000))"
    :return: a dict of filters
    """
    if filter_str is None:
        return {}

    if '(' not in filter_str and ')' not in filter_str:
        return make_lv1_filters(filter_str)

    list1 = []
    temp = ''
    for x in filter_str:
        if x == '(' and temp:
            list1.append(temp.strip())
            temp = ''
        temp += x
        if x == ')':
            list1.append(temp.strip())
            temp = ''
    list2 = []
    temp = []
    flag = False
    for x in list1:
        if flag and x not in ['(', ')']:
            temp.append(x)
        elif x not in ['(', ')']:
            list2.append(x)

        if x == '(':
            flag = True
        elif x == ')':
            flag = False
            list2.append(temp)

    return make_lv2_filters(list2)
