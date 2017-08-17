from tkinter import Tk

from interface.ui_root import CCManagerRoot


def ccmanager_main():
    root = Tk()
    root = CCManagerRoot(root)
    root.mainloop()


if __name__ == '__main__':
    ccmanager_main()
