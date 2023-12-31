# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: openopt\kernel\GUI.pyc
# Compiled at: 2012-12-08 11:04:59
TkinterIsInstalled = True
import platform
if platform.python_version()[0] == '2':
    try:
        from Tkinter import Tk, Toplevel, Button, Entry, Menubutton, Label, Frame, StringVar, DISABLED, ACTIVE
    except:
        TkinterIsInstalled = False

else:
    try:
        from tkinter import Tk, Toplevel, Button, Entry, Menubutton, Label, Frame, StringVar, DISABLED, ACTIVE
    except:
        TkinterIsInstalled = False

from threading import Thread
from openopt import __version__ as ooversion
from setDefaultIterFuncs import BUTTON_ENOUGH_HAS_BEEN_PRESSED, USER_DEMAND_EXIT
from ooMisc import killThread
from runProbSolver import finalShow

def manage(p, *args, **kwargs):
    p.isManagerUsed = True
    if not TkinterIsInstalled:
        p.err('Tkinter is not installed. If you have Linux you could try using "apt-get install python-tk"')
    p._args = args
    p._kwargs = kwargs
    for arg in args:
        if type(arg) == str or hasattr(arg, '__name__'):
            p.solver = arg
        elif arg in (0, 1, True, False):
            start = arg
        else:
            p.err('Incorrect argument for manage()')

    start = kwargs.pop('start', True)
    if 'solver' in kwargs.keys():
        p.solver = kwargs['solver']
    root = Tk()
    p.GUI_root = root
    p.GUI_buttons = {}
    Frame(root).pack(ipady=4)
    Label(root, text=' OpenOpt ' + ooversion + ' ').pack()
    Label(root, text=' Solver: ' + (p.solver if isinstance(p.solver, str) else p.solver.__name__) + ' ').pack()
    Label(root, text=' Problem: ' + p.name + ' ').pack()
    t = StringVar()
    t.set('      Run      ')
    RunPause = Button(root, textvariable=t, command=(lambda : invokeRunPause(p)))
    Frame(root).pack(ipady=8)
    RunPause.pack(ipady=15)
    p.GUI_buttons['RunPause'] = RunPause
    p.statusTextVariable = t

    def invokeEnough():
        p.userStop = True
        p.istop = BUTTON_ENOUGH_HAS_BEEN_PRESSED
        if hasattr(p, 'stopdict'):
            p.stopdict[BUTTON_ENOUGH_HAS_BEEN_PRESSED] = True
        p.msg = 'button Enough has been pressed'
        if p.state == 'paused':
            invokeRunPause(p, isEnough=True)
        else:
            RunPause.config(state=DISABLED)
            Enough.config(state=DISABLED)

    Frame(root).pack(ipady=8)
    Enough = Button(root, text='   Enough!   ', command=invokeEnough)
    Enough.config(state=DISABLED)
    Enough.pack()
    p.GUI_buttons['Enough'] = Enough

    def invokeExit():
        p.userStop = True
        p.istop = USER_DEMAND_EXIT
        if hasattr(p, 'stopdict'):
            p.stopdict[USER_DEMAND_EXIT] = True
        p.msg = 'user pressed Exit button'
        root.destroy()

    Frame(root).pack(ipady=8)
    Button(root, text='      Exit      ', command=invokeExit).pack(ipady=15)
    state = 'paused'
    if start:
        Thread(target=invokeRunPause, args=(p,)).start()
    root.mainloop()
    if hasattr(p, 'tmp_result'):
        r = p.tmp_result
        delattr(p, 'tmp_result')
    else:
        r = None
    return r


def invokeRunPause(p, isEnough=False):
    try:
        import pylab
    except:
        if p.plot:
            p.warn('to use graphics you should have matplotlib installed')
            p.plot = False

    if isEnough:
        p.GUI_buttons['RunPause'].config(state=DISABLED)
    if p.state == 'init':
        p.probThread = Thread(target=doCalculations, args=(p,))
        p.state = 'running'
        p.statusTextVariable.set('    Pause    ')
        p.GUI_buttons['Enough'].config(state=ACTIVE)
        p.GUI_root.update_idletasks()
        p.probThread.start()
    elif p.state == 'running':
        p.state = 'paused'
        if p.plot:
            pylab.ioff()
        p.statusTextVariable.set('      Run      ')
        p.GUI_root.update_idletasks()
    elif p.state == 'paused':
        p.state = 'running'
        if p.plot:
            pylab.ion()
        p.statusTextVariable.set('    Pause    ')
        p.GUI_root.update_idletasks()


def doCalculations(p):
    try:
        p.tmp_result = p.solve(*p._args, **p._kwargs)
    except killThread:
        if p.plot:
            if hasattr(p, 'figure'):
                pylab.ioff()
                pylab.close('all')


def invokeCommand(cw):
    exec cw.get()