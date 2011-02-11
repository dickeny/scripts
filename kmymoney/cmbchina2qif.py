#!/usr/bin/env python2
#-*- coding: UTF-8 -*-

def bill2qif(line):
    from datetime import datetime
    csv = [ val.lstrip() for val in line.split(';')]
    account = csv[0]
    date = datetime.strptime(csv[1], '%Y%m%d').strftime('%d.%m.%Y')
    bill_type = csv[2]
    bill_out = float(csv[3]) if csv[3] != '' else 0
    bill_in = float(csv[4]) if csv[4] != '' else 0
    bill_remain = float(csv[5])
    message = csv[6]
    label = message.split(' ')[0]
    out = 'D%s\nT%s\nL%s\nM%s\nC*\n^\n' % (date, bill_in - bill_out, label, message)
    return out

def convert(filename):
    print 'convert %s => %s.qif' % (filename, filename)
    fin = open(filename)
    fout = open(filename+'.qif', 'w')
    buf = '!Type:Bank\n^\n'
    for line in fin:
        if line.startswith('#'):
            continue
        buf += bill2qif(line)
    fout.write(buf)
    fout.close()

if __name__ == '__main__':
    from sys import argv
    for file in argv[1:]:
        convert(file)

