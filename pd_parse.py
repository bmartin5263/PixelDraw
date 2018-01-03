def parse(filename):
    filelines = open(filename, 'r').readlines()
    output = []
    currentMenu = {}
    currentElement = {}
    filetype = None
    for line in filelines:
        split = line.split()
        if len(split) > 0:
            sigil = split[0][0]
            sigilName = split[0][1:].lower()
            if currentMenu == {}:
                if sigil == '@':
                    if currentMenu != {}:
                        output.append(currentMenu)
                        currentMenu = {}
                    currentMenu['class'] = sigilName
                    currentMenu['name'] = split[1]
                    currentMenu['elements'] = []
                elif sigil == '?':
                    filetype = split[1]
            else:
                if sigil == '!':
                    if currentElement != {}:
                        currentMenu['elements'].append(currentElement)
                        currentElement = {}
                    currentElement['class'] = sigilName
                    try:
                        currentElement['name'] = split[1]
                    except IndexError:
                        pass
                elif sigil == '$':
                    value = split[1]
                    if currentElement == {}:
                        currentMenu[sigilName] = value
                    else:
                        currentElement[sigilName] = value
                elif sigil == '@':
                    if currentMenu != {}:
                        if currentElement != {}:
                            currentMenu['elements'].append(currentElement)
                            currentElement = {}
                        output.append(currentMenu)
                        currentMenu = {}
                    currentMenu['class'] = sigilName
                    currentMenu['name'] = split[1]
                    currentMenu['elements'] = []
                elif sigil == '#':
                    pass
    if currentElement != {}:
        currentMenu['elements'].append(currentElement)
    if currentMenu != {}:
        output.append(currentMenu)
    return output, filetype