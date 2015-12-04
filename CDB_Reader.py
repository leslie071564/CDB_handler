# -*-coding: utf-8 -*-
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os.path
import codecs
import cdb


class CDB_Reader(object):
    def __init__(self, keyMapFile, repeated_keys=False, numerical_keys=True):
        # the options.
        self.repeated_keys = repeated_keys
        self.numerical_keys = numerical_keys
        self.mapping = []

        dbdir = os.path.dirname(keyMapFile)
        basename = os.path.basename(keyMapFile)
        basename = re.sub("keymap", "", basename)

        CDB0 = "%s/%s%s" % (dbdir, basename, "0")
        if os.path.isfile(CDB0):
            self.mapping.append({'key': None, 'cdb': CDB0})

        # check for validity
        if os.path.isfile(keyMapFile) and os.path.getsize(keyMapFile) > 0:
            CDB1 = "%s/%s%s" % (dbdir, basename, "1")
            if not os.path.isfile(CDB1):
                sys.stderr.write("The size of the keymapfile is 0, but %s \
                exists. The size of the keymapfile should be more than 0!\n"
                                 % (CDB1))
                sys.exit(1)

        # parse the keymap file.
        f = codecs.open(keyMapFile, 'r', 'utf-8')
        for line in iter(f.readline, ''):
            line = line.strip()
            pattern = r"^(.+) ([^ ]+)$"
            if re.match(pattern, line):
                key, which_file = re.match(pattern, line).groups()
            else:
                sys.stderr.write("malformed keymap.\n")
                sys.exit(1)
            CDBi = str("%s/%s" % (dbdir, which_file))
            if os.path.isfile(CDBi):
                self.mapping.append({'key': key, 'cdb': CDBi})
            else:
                sys.exit(1)
        f.close()

    def get(self, searchKey, exhaustive=False):
        # exhaustive must be True if keys are not sorted in ascending order
        if exhaustive:
            for i in range(len(self.mapping)):
                nowCDB = self.mapping[i]['cdb']
                targetCDB = cdb.init(nowCDB)
                if self.repeated_keys:
                    value = targetCDB.getall(searchKey.encode('utf-8'))
                else:
                    value = targetCDB.get(searchKey.encode('utf-8'))
                if value:
                    return value
            return None
        else:
            nowCDB = self.mapping[0]['cdb']
            for i in range(1, len(self.mapping)):
                nowKey = self.mapping[i]['key']
                print nowKey
                print nowCDB
                if self.numerical_keys:
                    if int(searchKey) < int(nowKey):
                        break
                else:
                    if searchKey.encode('utf-8') < nowKey:
                        break
                nowCDB = self.mapping[i]['cdb']
            targetCDB = cdb.init(nowCDB)
            if self.repeated_keys:
                value = targetCDB.getall(searchKey.encode('utf-8'))
            else:
                value = targetCDB.get(searchKey.encode('utf-8'))
            return value
