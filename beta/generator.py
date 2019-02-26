#!/usr/bin/env python
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# *  Based on code by j48antialias:
# *  https://anarchintosh-projects.googlecode.com/files/addons_xml_generator.py

from __future__ import print_function
from os import walk, makedirs
from os.path import exists, join, dirname, abspath
from shutil import rmtree
import hashlib
from traceback import print_exc
from zipfile import ZipFile

OMIT_LINE = '<?xml'.encode('utf-8')


class Generator:
    '''
    Generates a new addons.xml file from each addons addon.xml file
    and a new addons.xml.md5 hash file. Must be run from the root of
    the checked-out repo.
    '''
    def __init__(self):
        # generate files
        self._generate_addons_file()
        # notify user
        print('Finished updating addons xml and md5 files')

    def _generate_addons_file(self):
        self.cwd = dirname(abspath(__file__))
        self.addons_xml = join(self.cwd, 'addons.xml')
        # Opening tag
        with open(self.addons_xml, 'wb') as f:
            f.write('<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'yes\'?>\n'.encode('utf-8'))
            f.write('<addons>\n'.encode('utf-8'))
        # loop thru and add each addons addon.xml file
        for root, dirs, files in walk(self.cwd):
            if root == self.cwd:
                continue
            for file in files:
                print('Processing file: %s' % file)
                if file.endswith('.zip'):
                    try:
                        self.unzip(root, file)
                    except:
                        # missing or poorly formatted addon.xml
                        print('Excluding %s' % root)
                        print_exc()
                if (not file.endswith('.md5') and
                        not exists(join(root, '%s.md5' % file))):
                    print('Calculating md5 for %s' % file)
                    self._generate_md5_file(root, file)
        # closing tag
        with open(self.addons_xml, 'ab') as f:
            f.write('</addons>\n'.encode('utf-8'))
        # MD5 of the generated addons.xml itself
        self._generate_md5_file(self.cwd, 'addons.xml')

    def unzip(self, root, file):
        temp_dir = join(root, 'temp')
        if not exists(temp_dir):
            makedirs(temp_dir)
        with ZipFile(join(root, file), 'r') as myzip:
            myzip.extractall(temp_dir)
        for new_root, dirs, files in walk(temp_dir):
            for file in files:
                if file == 'addon.xml':
                    self.build_xml(new_root, file)

        rmtree(temp_dir)

    def build_xml(self, root, file):
        # create path
        _path = join(root, file)
        with open(self.addons_xml, 'ab') as f1:
            with open(_path, 'rb') as f2:
                for line in f2.readlines():
                    if not line.startswith(OMIT_LINE):
                        f1.write(line)

    def _generate_md5_file(self, root, file):
        _path = join(root, file)
        # create a new md5 hash
        m = self.md5(_path)

        # save file
        try:
            self._save_file(m.encode('UTF-8'), '%s.md5' % _path)
        except:
            # oops
            print('An error occurred creating %s file!'
                  % join(_path, '.md5'))

    def md5(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _save_file(self, data, file):
        with open(file, 'wb') as fo:
            fo.write(data)
            fo.write('\n'.encode('UTF-8'))


if __name__ == '__main__':
    # start
    Generator()
