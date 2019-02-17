import re

upper_word_match = re.compile(r'([A-Z]+[a-z]+)')
lower_word_match = re.compile('^[a-z]+')


def upper_first_letter(_str):
    return _str[0].upper() + _str[1:]


def add_underscore(_str: str):
    """transform fileLoggingHandler to file_logging_handler"""
    if not _str.strip():
        yield ''
    if len(_str) > 1:
        yield _str[0].lower()
        for char in _str[1:]:
            if char.isupper():
                yield '_'
                yield char.lower()
            else:
                yield char
    else:
        yield _str.lower()


def camel_case_2_underscore_case(name: str):
    _match = upper_word_match.findall(name)
    if not _match or len(_match) == 1:
        return name
    first_word_match = lower_word_match.match(name)
    if first_word_match:
        first_word = first_word_match.group() + '_'
    else:
        first_word = ''
    new_name = first_word + '_'.join(item.lower() for item in _match)
    return new_name


def underscore_case_2_camel_case(name: str):
    name_list = name.split('_')
    if 1 == len(name_list):
        return name
    name_list = [item for item in name_list if item.strip()]
    new_name = name_list[0] + ''.join(map(upper_first_letter, name_list[1:]))
    return new_name


if __name__ == '__main__':
    print(camel_case_2_underscore_case('printKeyValueUU'))
    print(camel_case_2_underscore_case('printKeyValue'))
    print(camel_case_2_underscore_case('nihao'))
    print(underscore_case_2_camel_case('__Iam_test'))
    print(underscore_case_2_camel_case('print_key_value'))
    print(underscore_case_2_camel_case('I_am_go_ing__home'))
    print(''.join(add_underscore('printKeyValueUU')))
