"""
    this module is a driver code for testing Miniature Simulator module
    imports Simulator from core.py
    for more details about project read README.md
"""

from sys import argv
from PyQt5.QtWidgets import QApplication, QWidget
from core import Simulator

if argv[0] != "simulate.py":
    exit(0)

try:
    # read machine code from input :
    asm = open(argv[1], "r").readlines()
    app = QApplication(argv)
    # pass a list of code lines through Simulator class
    simulate = Simulator(asm)
    exit(app.exec_())

except ValueError as error:
    open("log_" + argv[1], "w").write("# " + str(error))
    print(error)

