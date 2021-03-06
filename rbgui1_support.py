#! /usr/bin/env python
#
# Support module generated by PAGE version 4.5
# In conjunction with Tcl version 8.6
#    Dec 17, 2015 09:35:09 PM
# This module implements the event handlers for the Smart Wheel Module and
# implements some threads to refresh the GUI with data from the Smart Wheel rbha module
# Implemented by HJ Kiela Opteq mechatronics BV Febr 2016

import sys
import rbha          # Rosbee hardware abstraction
import threading
import time
import bits
import About
import comportconfig_support
import comportconfig

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

try:
    import ttk
    py3 = 0
except ImportError:
    import tkinter.ttk as ttk
    py3 = 1

# ---------------- variables connected to sliders --------------------
class twvar:              # variables connnected to main window
    Force_Token_var = 0

wvar = twvar      # declare main window variables
debug = False

# Initialize main windo variables
# Note that the type definitions are important for porper use by the window objects in ttk
def set_Tk_var():
    if debug:
        print(" Init Tkvar")
    global wvar
    wvar.gui_set_direction = StringVar()
    wvar.Force_Token_var = IntVar()
    wvar.ts_speed_value = DoubleVar()
    wvar.ts_direction_value = DoubleVar()
    wvar.gui_set_direction = StringVar()
    wvar.gui_act_direction = StringVar()
    wvar.gui_setspeed = StringVar()
    wvar.gui_actspeed = StringVar()
    wvar.gui_radpersec = StringVar()
    wvar.gui_timers = StringVar()
    wvar.gui_counters = StringVar()
    wvar.gui_version = StringVar()
    wvar.gui_statushex = StringVar()
    wvar.gui_errorhex = StringVar()
    wvar.gui_actspeedmpersec = StringVar()

    wvar.Cs0var = IntVar()
    wvar.Cs1var = IntVar()
    wvar.Cs2var = IntVar()
    wvar.Cs3var = IntVar()
    wvar.Cs4var = IntVar()
    wvar.Cs5var = IntVar()
    wvar.Cs6var = IntVar()
    wvar.Cs7var = IntVar()
    wvar.Cs8var = IntVar()
    wvar.Cs9var = IntVar()
    wvar.Cs10var = IntVar()
    wvar.Cs11var = IntVar()
    wvar.Cs12var = IntVar()
    wvar.Cs13var = IntVar()
    wvar.Cs14var = IntVar()
    wvar.Cs15var = IntVar()


# ------------- Various event handlers ----------------
def TODO():
    print('gui_support.TODO')
    sys.stdout.flush()


def do_about():
    About.create_About_GUI(root)
#    About.vp_start_gui(root)

# ---------------- Update main window title ------------------
def updatetitle(windowtitle):
    global root
    root.title(windowtitle)
# end: updatetitle

# ----- Open serial port dialog --)
def do_SerialPortConfig():
    comportconfig.create_ComportConfig(root)

# --------- Open connection with serial port -----------------
def do_connect_serial():
    global t
    print('gui1_support.do_connect')
    if rbha.isportopen():   # close comport
        rbha.close_serial()
        w.txt_connect_indicator.configure(background="white")
        w.btn_connect.configure(text='''Connect''')
        updatetitle('Opteq Rosbee GUI V1')
    else:  # open com port
        rbha.open_serial()
        serialconfig = comportconfig_support.Readconfig()
        w.txt_connect_indicator.configure(background="green")
        w.btn_connect.configure(text='''Diconnect''')
        connectionstr = rbha.get_connection_info()
        print('connection info _support' ,connectionstr)
        updatetitle("Opteq Rosbee GUI V1-->" + serialconfig['baudrate'] + ',' + serialconfig['comport'])
    sys.stdout.flush()
# end: do_connect


def Do_Stop():  # event handler for stop button wheel speed
    do_new_speed(0)
    wvar.ts_speed_value.set(0)


def Do_Center():  # event handler for center button steer
    do_new_direction(0)
    wvar.ts_direction_value.set(0)


def do_new_direction(new_direction):
#def do_new_direction():
#    rbha.rb1.setsteer = int(float(new_direction))
    rbha.rb1.setsteer = float(new_direction) / 40  #new rotational speed in radians. per second
#    rbha.rb1.setpos = int(wvar.ts_direction_value)
#    rbha.sendnewsetpoints()
    if debug:
        print('gui_support.do_new_direction ' + str(new_direction) + ' ' + str(rbha.rb1.setsteer))
    sys.stdout.flush()


def do_new_speed(new_speed):
#    rbha.rb1.setspeed = int(float(new_speed))
    rbha.rb1.setspeed = float(new_speed)/250  # new speed in m/s
#    rbha.sendnewsetpoints()
    if debug:
        print('gui_support.do_new_speed ' + str(new_speed))
    sys.stdout.flush()


def do_reset():
    rbha.do_reset()
    print('gui_support.do_reset')
    sys.stdout.flush()


def do_enable():
    rbha.do_enable()
    wvar.ts_speed_value.set(rbha.rb1.setspeed)
    wvar.ts_direction_value.set(rbha.rb1.setsteer)

    print('gui_support.do_enable ' + str(rbha.rb1.enable))


def HandleForceToken():
    global wvar
    if (wvar.Force_Token_var.get()==1):
        w.btn_enable.configure(state=ACTIVE)
    else:
        if rbha.rb1.enable:
          rbha.do_enable()  # disable if enabled
        w.btn_enable.configure(state=DISABLED)

    print('Force token changed ' + str(wvar.Force_Token_var.get()) )

#  menu item exit
def do_exit():
    if rbha.rb1.enable:
       rbha.do_enable()  # disable if enabled
    destroy_window()


def do_resetminmax():    # Reset min max adc
    rbha.do_reset_minmax()


# ---------- Init is called by UDPGUI at initialisation -----------
def init(top, gui, arg=None):
    global w, top_level, root
    w = gui
    top_level = top
    root = top
    updatetitle('Opteq UDPGUI V2')
    t = threading.Thread(target=do_update)      # create read thread to refresh form status
    t.setDaemon(1)
    t.start()
# end: init()


def destroy_window():
    # Function which closes the window.
    global top_level
    top_level.destroy()
    top_level = None


#------------- Run once after initialisation -----------------
def run_once():
    global wvar
    print('Run once gui')
    if rbha.isportopen():
        wvar.gui_version = rbha.rb1.version

#------------- Run periodic functions-----------------
# Periodic update of gui based on refreshed data from hardware abstraction
def do_update():
    global wvar
    gui_refreshtime = 0.2  # sec
    while 1:
        if 1: #rbha.isportopen():
            if debug:
                print('Thread update gui')
            # if rbha.rb1.newlabels:       # check if status labels refreshed
            #     create_status_checks
            #     rbha.rb1.newlabel=False

            # if rbha.isportopen():
            # w.entry_actspeed.insert(0,str(rbha.rb1.actspeed))
            wvar.gui_actspeed.set(str(rbha.rb1.pf_actwheelvel[0]) + ' ' + str(rbha.rb1.pf_actwheelvel[1]))
            wvar.gui_setspeed.set(str(rbha.rb1.setspeed))
            wvar.gui_act_direction.set(rbha.rb1.actsteerpos)
            wvar.gui_set_direction.set(rbha.rb1.setsteer)
            wvar.gui_counters.set('PID: ' + str(rbha.rb1.pid_cntr) + ' plc '  + str(rbha.rb1.plc_cntr))
            wvar.gui_timers.set('PID: %4.1f' % (rbha.rb1.PIDtime*1000) + ' %4.1f ' % (rbha.rb1.pid_leadtime*1000) + 'plc: %4.1f' % (rbha.rb1.plc_time*1000))
            wvar.gui_radpersec.set('%6.3f' %(rbha.rb1.actrotvel_radians))

            wvar.gui_actspeedmpersec .set('%6.3f' %(rbha.rb1.actwheelvelmeterpersec[0]))
            # gui_statushex.set('x00')
            wvar.gui_statushex.set(hex(rbha.rb1.status))
            wvar.gui_version.set(str(rbha.rb1.version[0] + ' ' + rbha.rb1.version[1] + ' ' + rbha.rb1.version[2]))
            if (rbha.rb1.enable):                   # set enable led
                w.entry_enable.configure(background="green")
            else:
                w.entry_enable.configure(background="red")

            if bits.testbit2int(rbha.rb1.status,15):              # set reset led red if there is an error
                w.entry_reset.configure(background="red")
                wvar.ts_speed_value.set(0)                        # force speed and direction sliders at 0 during error
                wvar.ts_direction_value.set(0)
            else:
                w.entry_reset.configure(background="green")

            wvar.Cs0var.set(bits.testbit2int(rbha.rb1.status, 0))
            # wvar.Cs1var.set(bits.testbit2int(rbha.rb1.status, 1))
            # wvar.Cs2var.set(bits.testbit2int(rbha.rb1.status, 2))
            wvar.Cs3var.set(bits.testbit2int(rbha.rb1.status, 3))
            wvar.Cs4var.set(bits.testbit2int(rbha.rb1.status, 4))
            wvar.Cs5var.set(bits.testbit2int(rbha.rb1.status, 5))
            # wvar.Cs6var.set(bits.testbit2int(rbha.rb1.status, 6))
            wvar.Cs7var.set(bits.testbit2int(rbha.rb1.status, 7))
            # wvar.Cs8var.set(bits.testbit2int(rbha.rb1.status, 8))
            # wvar.Cs9var.set(bits.testbit2int(rbha.rb1.status, 9))
            # wvar.Cs10var.set(bits.testbit2int(rbha.rb1.status, 10))
            wvar.Cs11var.set(bits.testbit2int(rbha.rb1.status, 11))
            # wvar.Cs12var.set(bits.testbit2int(rbha.rb1.status, 12))
            wvar.Cs13var.set(bits.testbit2int(rbha.rb1.status, 13))
            wvar.Cs14var.set(bits.testbit2int(rbha.rb1.status, 14))
            wvar.Cs15var.set(bits.testbit2int(rbha.rb1.status, 15))

            w.lb_adc.delete(0, END)        # erase text field for new round
            dline = "         Act    Min    Max"
            w.lb_adc.insert(END, dline + '\r\n' )

            for index in range(rbha.rb1.n_adc_channels):         # print adc values
                dline = str(index) + ' {:>5}'.format(rbha.rb1.adclabels[index]) + ' %6.3f'   % (rbha.rb1.adc_avg[index])
                dline = dline + ' %6.3f'   % (rbha.rb1.adc_min[index])
                dline = dline + ' %6.3f'   % (rbha.rb1.adc_max[index])
                w.lb_adc.insert(END, dline)

#' ' + str(rbha.rb1.gyro_sensitivity) +
            w.lb_adc.insert(END, '' )
            dline = 'Gyro ' + str(rbha.rb1.pf_gyroZ) +  ' %6.3f' % (rbha.rb1.gyroZ) + ' %6.3f' % (rbha.rb1.gyroZrad)
            w.lb_adc.insert(END, dline)
            dline = 'Proptime ' + str(rbha.rb1.proptime)
            w.lb_adc.insert(END, dline)
            dline = 'Actpos ' + str(rbha.rb1.pf_actwheelpos[0]) + ' ' + str(rbha.rb1.pf_actwheelpos[1])
            w.lb_adc.insert(END, dline)
            dline = 'deltatime ' + str(rbha.rb1.deltatime) + ' ' + str(rbha.rb1.acttime) + ' ' + str(rbha.rb1.lasttime)
            w.lb_adc.insert(END, dline)
            dline = 'vel %6.3f'  %(rbha.rb1.actwheelvel[0]) + ' %6.3f' %(rbha.rb1.actwheelvel[1])
            w.lb_adc.insert(END, dline)
            dline = 'cnts2mps %6.3f'  %(rbha.rb1.countsperpid_to_meterpersec) + ' %6.3f' %(rbha.rb1.actwheelvelmeterpersec[0]) + ' %6.3f' %(rbha.rb1.actrotvel_radians)
            w.lb_adc.insert(END, dline)

        if debug:
            time.sleep(gui_refreshtime / 10)         # wait for next screen refresh period
        else:
            time.sleep(gui_refreshtime)         # wait for next screen refresh period

