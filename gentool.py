#!/usr/bin/env python3

##  rFactor .gen file manipulation tool
##  Copyright (C) 2013 Ingo Ruhnke <grumbel@gmail.com>
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import re
import os
import ntpath

keyvalue_regex = re.compile(r'^\s*([^=]+)\s*=([^\s]+)+')
comment_regex = re.compile(r'(.*?)(//.*)')
section_start_regex = re.compile(r'\s*{')
section_end_regex = re.compile(r'\s*}')

def process_vehfile(filename):
    # print("processing", filename)
    graphics_file = None

    with open(filename, 'r', encoding='latin-1') as fin:
        for orig_line in fin.read().splitlines():
            line = orig_line

            m = comment_regex.match(line)
            if m:
                comment = m.group(2)
                line = m.group(1)
            else:
                comment = None

            m = keyvalue_regex.match(line)
            if m:
                key, value = m.group(1), m.group(2)
                if key.lower() == "graphics":
                    graphics_file = value.strip()

        return graphics_file

class GenParser:
    def __init__(self):
        pass

    def on_key_value(self, key, value, comment, orig):
        pass

    def on_section_start(self, comment, orig):
        pass

    def on_section_end(self, comment, orig):
        pass

    def on_unknown(self, orig):
        pass

class InfoGenParser(GenParser):
    def __init__(self):
        self.section = False
        self.search_path = []
        self.mas_files = []

    def on_key_value(self, key, value, comment, orig):
        if not self.section:
            if key.lower() == "masfile":
                self.mas_files.append(value)
            elif key.lower() == "searchpath":
                self.search_path.append(value)
            else:
                pass

    def on_section_start(self, comment, orig):
        self.section = True

    def on_section_end(self, comment, orig):
        self.section = False

class SearchReplaceGenParser(GenParser):
    def __init__(self):
        self.section = False

    def on_key_value(self, key, value, comment, orig):
        print(orig)

    def on_section_start(self, comment, orig):
        self.section = True
        print(orig)

    def on_section_end(self, comment, orig):
        self.section = False
        print(orig)

def process_genfile(filename, veh_directory, parser):
    # print("processing", filename)
    with open(filename, 'r', encoding='latin-1') as fin:
        for orig_line in fin.read().splitlines():
            line = orig_line

            m = comment_regex.match(line)
            if m:
                comment = m.group(2)
                line = m.group(1)
            else:
                comment = None

            m = keyvalue_regex.match(line)
            m_sec_start = section_start_regex.match(line)
            m_sec_stop  = section_end_regex.match(line)
            if m:
                key, value = m.group(1), m.group(2)
                parser.on_key_value(key, value, comment, orig_line)
            elif m_sec_start:
                parser.on_section_start(comment, orig_line)
            elif m_sec_stop:
                parser.on_section_end(comment, orig_line)
            else:
                parser.on_unknown(orig_line)

def find_file_backwards(dir, gen):
    filename = os.path.join(dir, gen)
    if os.path.exists(filename):
        return filename
    elif dir and dir != '/':
        return find_file_backwards(os.path.dirname(dir), gen)
    else:
        raise Exception("error: couldn't find .gen file '%s'" % gen)

def find_vehdir(path):
    m = re.match(r'^(.*GameData/Vehicles)', path, re.IGNORECASE)
    if m:
        print(m.group(1))
        return m.group(1)
    else:
        raise Exception("couldn't locate <VEHDIR> in %s" % path)

def verify_gen(search_path, mas_files, vehdir, teamdir):
    for mas in mas_files:
        pass

def process_directory(directory):
    gen_files = []
    veh_files = []

    for path, dirs, files in os.walk(directory):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext == ".gen":
                gen_files.append(os.path.join(path, fname))
            elif ext == ".veh":
                veh_files.append(os.path.join(path, fname))

    print(veh_files)
    for veh in veh_files:
        try:
            teamdir = os.path.dirname(veh)
            vehdir  = find_vehdir(os.path.dirname(veh))

            gen = process_vehfile(veh)
            gen = find_file_backwards(os.path.dirname(veh), gen)
            print("veh:", veh)
            print("gen:", gen)
            info = InfoGenParser()
            process_genfile(gen, os.path.dirname(veh), info)
            print("  SearchPath:", info.search_path)
            print("    MasFiles:", info.mas_files)
            print("    <VEHDIR>:", vehdir)
            print("   <TEAMDIR>:", teamdir)
            verify_gen(info.search_path, info.mas_files, vehdir, teamdir)
            print()
        except Exception as e:
            print("error:", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='rFactor .veh/.gen processor')
    parser.add_argument('DIRECTORY', action='store', type=str,
                        help='directory containing .gen and .veh files')
    parser.add_argument('-c', '--check', action='store_true', default=False,
                        help="check the file for errors")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="be more verbose")
    parser.add_argument('--add-searchpath', metavar="PATH",
                        help="be more verbose")
    args = parser.parse_args()

    process_directory(args.DIRECTORY)

# EOF #
