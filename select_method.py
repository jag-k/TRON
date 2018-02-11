def select(title="", *quest, numb=True, default=True, lang='eng'):
    """
    :param title: Вопрос
    :param quest: Варианты ответа
    :param numb: Нумеровать ли вопросы?
    :param default: Что будет если строка ввода будет пуста (если в quest пусто) (действие по умолчанию)?
    :param lang: Язык (eng/rus)
    :param out: Вывод (по умолчанию в консоль)
    :return: Bool (если в quest пусто) или (элемент quest, индекс элемента quest) (если в quest есть элементы)
    """
    out = None
    yes = ['y', 'yes', 'д', 'да']
    no = ['n', 'no', 'н', 'нет']
    if quest:
        if len(quest) == 1:
            return quest[0], 0
        print(title + ':', file=out) if title else False
        for i in range(len(quest)):
            print('\t{}{}'.format(str(i + 1) + ') ' if numb else "", quest[i] + (';' if i != len(quest) else '.')),
                  file=out)
        while True:
            t = input('1-' + str(len(quest)) + ': ')
            if t.isdigit():
                if 0 < int(t) < len(quest) + 1:
                    return quest[int(t) - 1], int(t) - 1
    else:
        print(title, end=' ', file=out)
        if lang.lower() == 'eng' or lang.lower() == 'en':
            answer = '(Y/n)' if default else '(y/N)'
        elif lang.lower() == 'rus' or lang.lower() == 'ru':
            answer = '(Д/н)' if default else '(д/Н)'
        else:
            answer = '(Y/n)' if default else '(y/N)'
        while True:
            t = input(answer + ': ')
            if not t:
                return default
            elif t:
                if t.lower() in yes:
                    return True
                elif t.lower() in no:
                    return False
