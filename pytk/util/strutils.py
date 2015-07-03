

#-------------------------------------------------------------------------------
# strings manipulation utilities
#-------------------------------------------------------------------------------

def upperFirst(w):
    return w[0].upper() + w[1:]

def lowerFirst(w):
    return w[0].lower() + w[1:]

def wordSplit(s, digits=False):
    '''
    Author: http://stackoverflow.com/users/1850574/jdavidls
    
    A very 'low level' implementation of a simple state machine (bitfield state machine).
    This is not an elegant method and possibly the most anti-pythonic mode to resolve this. 
    However, 're' module also implements a too complex state machine to resolve this simple task.
    
        state bits:
        0: no yields
        1: lower yields
        2: lower yields - 1
        4: upper yields
        8: digit yields
        16: other yields
        32 : upper sequence mark
    '''

    digit_state_test = 8 if digits else 0
    si, ci, state = 0, 0, 0 # start_index, current_index

    for c in s:

        if c.islower():
            if state & 1:
                yield s[si:ci]
                si = ci
            elif state & 2:
                yield s[si:ci - 1]
                si = ci - 1
            state = 4 | 8 | 16
            ci += 1

        elif c.isupper():
            if state & 4:
                yield s[si:ci]
                si = ci
            if state & 32:
                state = 2 | 8 | 16 | 32
            else:
                state = 8 | 16 | 32

            ci += 1

        elif c.isdigit():
            if state & digit_state_test:
                yield s[si:ci]
                si = ci
            state = 1 | 4 | 16
            ci += 1

        else:
            if state & 16:
                yield s[si:ci]
            state = 0
            ci += 1  # eat ci
            si = ci
        #print(' : ', c, bin(state))
    if state:
        yield s[si:ci]

def labelify(s):
    return " ".join((upperFirst(w) for w in wordSplit(s)))

def underJoin(iterable):

    if isinstance(iterable, basestring):
        return iterable

    return "_".join(iterable)

def camelJoin(iterable):

    if isinstance(iterable, basestring):
        return iterable

    return "".join((upperFirst(w) if i > 0 else w.lower() for i, w in enumerate(iterable)))


