#!/usr/bin/env python3

# rFactorTools GUI
# Copyright (C) 2014 Ingo Ruhnke <grumbel@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from tkinter import *
import tkinter.filedialog
import tkinter.messagebox 
import PIL.Image
import PIL.ImageTk
import traceback
import argparse

import rfactortools


welcome_text = \
"""            ..:: rFactor to Game Stock Car 2013 ::..
            ========================================

This application allows you to convert rFactor mods so that they can
be used with Game Stock Car 2013. Conversation is for most part
automatic, but some issues may remain, the file FAQ.md explains how to
fix or work around some of them

To convert a mod:

1) extract it or if it comes as .exe install it into an empty directory

2) select the directory where you installed the mod as "Input"

3) select the directory where you want the conversion to be copied to
   as "Output". Installing directly into the GSC2013 is not
   recommended, use an empty directory instead.

4) Hit the "Convert" button and wait a minute or two.

5) Once the conversion is finished copy the mod over to the GSC2013
   directory

Car mods will show up in the same class as the Mini Challenge.


Options:
--------

Unique Team Names:
Adds a suffix to the 'Team' name in .veh files to make them unique and
avoid conflicts with other mods


Force Track Thumbnail:
Always generate a new track thumbnail, ignoring the one from the
original mod


Disclaimer:

rfactortools is a homebrew tool collection for rFactor, Race07 and
GSC2013 and in no way affiliated with Image Space Incorporated, SimBin
Studios or Reiza Studios.
"""


def createDirectoryEntry(frame, name, row):
    directory_label = Label(frame, text=name)
    directory_label.grid(column=0, row=row, sticky=N+S+E, pady=4)

    directory = StringVar()
    directory_entry = Entry(frame, textvariable=directory)
    directory_entry.grid(column=1, row=row, sticky=N+S+W+E, pady=4)

    directory_button = Button(frame)
    directory_button["text"] = "Browse"
    directory_button.grid(column=2, row=row, sticky=N+S, pady=4)
    directory_button["command"] =  lambda: do_ask_directory(directory)

    return directory


def do_ask_directory(directory):
    d = tkinter.filedialog.askdirectory()
    if d:
        directory.set(d)


class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.source_directory = None
        self.target_directory = None

        self.createWidgets()
        self.pack(anchor=CENTER, fill=BOTH, expand=1)

    def createWidgets(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure(0, weight=1)


        self.photo = PIL.ImageTk.PhotoImage(PIL.Image.open("logo.png"))
        self.photo_label = Label(self, image=self.photo, anchor=N, width=256, height=256)
        self.photo_label["bg"] = "black"
        self.photo_label.grid(column=0, row=0, sticky=N+S+W+E)
        self.photo_label.winfo_height = 256

        self.scrollbar = Scrollbar(self)
        self.scrollbar.grid(column=2, row=0, sticky=N+S)

        self.text = Text(self, yscrollcommand=self.scrollbar.set)
        self.text.insert(END, welcome_text)
        self.text.config(state=DISABLED)
        self.text.grid(column=1, row=0, sticky=N+S+W+E)
        self.scrollbar.config(command=self.text.yview)

        self.directory_frame = Frame(self)
        self.directory_frame.grid_columnconfigure(1, weight=1)
        self.source_directory = createDirectoryEntry(self.directory_frame, "Input:", 0)
        self.target_directory = createDirectoryEntry(self.directory_frame, "Output:", 1)
        self.target_directory.set("build/")
        self.directory_frame.grid(column=0, row=1, columnspan=3, sticky=W+E, padx=8, pady=4)


        self.option_frame = Frame(self)
        self.option_frame.grid(column=0, row=2, columnspan=3, sticky=W+E+N+S)

        self.unique_team_names = BooleanVar(value=True)
        self.unique_team_names_checkbox = Checkbutton(self.option_frame, text="Unique Team Names", variable=self.unique_team_names)
        self.unique_team_names_checkbox.grid(column=0, row=0)

        self.force_track_thumb = BooleanVar(value=False)
        self.force_track_thumb_checkbox = Checkbutton(self.option_frame, text="Force Track Thumbnail", variable=self.force_track_thumb)
        self.force_track_thumb_checkbox.grid(column=1, row=0)

        self.button_frame = Frame(self)
        self.button_frame.grid(column=0, row=3, columnspan=3, sticky=W+E+N+S)

        self.confirm_button_frame = Frame(self.button_frame)
        self.confirm_button_frame.pack(side=RIGHT)

        self.tool_button_frame = Frame(self.button_frame)
        self.tool_button_frame.pack(side=LEFT)

        self.vehtree_btn = Button(self.tool_button_frame)
        self.vehtree_btn["text"] = ".veh tree"
        self.vehtree_btn["command"] =  self.do_veh_tree
        self.vehtree_btn.grid(column=0, row=0, sticky=S, pady=8, padx=8)

        self.veh_btn = Button(self.tool_button_frame)
        self.veh_btn["text"] = ".veh check"
        self.veh_btn["command"] =  self.do_veh_check
        self.veh_btn.grid(column=1, row=0, sticky=S, pady=8, padx=8)

        self.gen_btn = Button(self.tool_button_frame)
        self.gen_btn["text"] = ".gen check"
        self.gen_btn["command"] =  self.do_gen_check
        self.gen_btn.grid(column=2, row=0, sticky=S, pady=8, padx=8)

        self.cancel_btn = Button(self.confirm_button_frame)
        self.cancel_btn["text"] = "Quit"
        self.cancel_btn["command"] =  self.quit
        self.cancel_btn.grid(column=3, row=0, sticky=S, pady=8, padx=8)

        self.convert_btn = Button(self.confirm_button_frame)
        self.convert_btn["text"] = "Convert"
        self.convert_btn["command"] =  self.do_conversion
        self.convert_btn.grid(column=4, row=0, sticky=S, pady=8, padx=8)

    def do_conversion(self):
        if not self.source_directory.get():
            tkinter.messagebox.showerror("Input directory not selected", 
                                   "Input directory not selected",
                                   parent=self)

        elif not self.target_directory.get():
            tkinter.messagebox.showerror("Error: Output directory not selected", 
                                   "Output directory not selected", 
                                   parent=self)

        else:
            print("Source: %s" % self.source_directory.get())
            print("Target: %s" % self.target_directory.get())

            try:
                cfg = rfactortools.rFactorToGSC2013Config()
                cfg.unique_team_names = self.unique_team_names.get()
                cfg.force_track_thumbnails = self.force_track_thumb.get()

                converter = rfactortools.rFactorToGSC2013(self.source_directory.get(), cfg)
                converter.convert_all(self.target_directory.get())
                print("-- rfactor-to-gsc2013 conversion complete --")

                tkinter.messagebox.showinfo("Conversion finished",
                                            "Conversion finished",
                                            parent=self)
            except Exception as e:
                tb = traceback.format_exc()
                print(tb)
                tkinter.messagebox.showerror("Conversion failed", 
                                             "Conversion failed with:\n\n%s" % tb,
                                             parent=self)
            

    def do_veh_tree(self):
        print("--- veh tree: start ---")
        path = self.target_directory.get()
        files = rfactortools.find_files(path, ".veh")
        vehs = [rfactortools.parse_vehfile(filename) for filename in files]
        rfactortools.print_veh_tree(vehs)
        print("--- veh tree: end ---")

    def do_veh_check(self):
        print("--- veh check: start ---")
        path = self.target_directory.get()
        files = rfactortools.find_files(path, ".veh")
        vehs = [rfactortools.parse_vehfile(filename) for filename in files]
        rfactortools.print_veh_info(vehs)
        print("--- veh check: end ---")

    def do_gen_check(self):
        print("--- gen check: start ---")
        path = self.target_directory.get()
        rfactortools.process_gen_directory(path, False)
        print("--- gen check: end ---")


def main():
    parser = argparse.ArgumentParser(description='rFactor to GSC2013 converter')
    parser.add_argument('INPUTDIR', action='store', type=str, nargs='?',
                        help='directory containing the mod')
    parser.add_argument('OUTPUTDIR', action='store', type=str, nargs='?',
                        help='directory where the conversion will be written')
    args = parser.parse_args()

    root = tkinter.Tk()
    root.wm_title("rFactor to Game Stock Car 2013 Mod Converter V0.1.2")
    root.minsize(640, 400)
    app = Application(master=root)

    if args.INPUTDIR is not None:
        app.source_directory.set(args.INPUTDIR)

    if args.OUTPUTDIR is not None:
        app.target_directory.set(args.OUTPUTDIR)

    app.mainloop()


if __name__ == "__main__":
    main()

# EOF #
