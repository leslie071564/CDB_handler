#-*-coding: utf-8 -*-
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os.path
import codecs
import cdb

class CDB_Reader(object):
    def __init__(self, keyMapFile, repeated_keys=False, numerical_keys=True):
        #the options.
        self.repeated_keys = repeated_keys
        self.numerical_keys = numerical_keys
        self.mapping = []
        
        dbdir = os.path.dirname(keyMapFile)
        basename = os.path.basename(keyMapFile)
        basename = re.sub("keymap", "", basename)

        CDB0 = "%s/%s%s" % (dbdir, basename, "0")
        if os.path.isfile(CDB0):
            self.mapping.append({'key':None, 'cdb':CDB0})

        #check for validity
        if os.path.isfile(keyMapFile) and os.path.getsize(keyMapFile) > 0:
            CDB1 = "%s/%s%s" % (dbdir, basename, "1")
            if not os.path.isfile(CDB1):
                sys.stderr.write("The size of the keymapfile is 0, but %s exists. The size of the keymapfile should be more than 0!\n" % (CDB1))
                sys.exit(1)

        #parse the keymap file.
        f = codecs.open(keyMapFile, 'r', 'utf-8')
        for line in iter(f.readlines()):
            line = line.strip()
            pattern = r"^(.+) ([^ ]+)$"
            if re.match(pattern, line):
                key, which_file = re.match(pattern, line).groups()
            else :
                sys.stderr.write("malformed keymap.\n")
                sys.exit(1)
            CDBi = str("%s/%s" % (dbdir, which_file))
            if os.path.isfile(CDBi):
                self.mapping.append({'key':key, 'cdb':CDBi})
            else :
                sys.exit(1)
        f.close()


    def get(self, searchKey, exhaustive=False):
        if exhaustive:
            for i in range(len(self.mapping)):
                nowCDB = self.mapping[i]['cdb']
                value = nowCDB.get(searchKey)
                if value: return value
            return None
        else:
            nowCDB = self.mapping[-1]['cdb']
            for i in range(1, len(self.mapping)):
                nowKey = self.mapping[i]['key']
                if searchKey.encode('utf-8') < nowKey :
                    nowCDB = self.mapping[i-1]['cdb']
                    break
            targetCDB = cdb.init(nowCDB)
            value = targetCDB.getall(searchKey.encode('utf-8')) if self.repeated_keys else targetCDB.get(searchKey.encode('utf-8'))
            return value


if __name__ == "__main__":
    test_str = u"乗る/のる-日帰り/ひがえり+湯/ゆ|ヲ|家族/かぞく|デ|楽しむ/たのしむ"
    PA_PAIR_REL = "/data/kohama/InferenceRuleAcquisitionDB/pa_pairs_relation_db/pa_pairs_relation.cdb.keymap"
    SID2PA = "/data/kohama/InferenceRuleAcquisitionDB/sid2pa/sid2pa.cdb.keymap"

    padb = CDB_Reader(PA_PAIR_REL)
    stdb = CDB_Reader(SID2PA)
    result = padb.get(test_str)
    print result
    key2 = "%s:" % (result.split(":")[0])
    print stdb.get(key2.decode('utf-8'))