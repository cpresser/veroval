#!/usr/bin/env python3
import serial
import binascii
import csv

data_entry_len = 14
data_offset = 3
req1 = b"\xA5\xF9\x01\x01\xFB"
req2 = b"\xA6\xF9\x01\x01\xFB"

# open serial port
s = serial.Serial("/dev/ttyUSB0", 19200)
s.timeout = 1
# send a magic request (sniffed from the windows software)
s.write(req1)
# read lots of bytes
ans = s.read(1024 * 16)
s.write(req2)
s.close()

if len(ans) < 2:
  print("no answer received. your device might have powered off.")
  quit()

# calculate how many answer items we got
n = int((len(ans) - data_offset) / data_entry_len)
n2 = ans[2]

print("Answer w/o checksum: " + binascii.hexlify(ans[:-1]).decode())
print("Checksum is: 0x%02x" % ord(ans[-1:]))

print ("got %d/%d entrys\n" % (n, n2))

with open('veroval.csv', 'w', newline='') as csvfile:
  csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
  csvwriter.writerow(["user", "year", "month", "hour", "minute", "sys", "dia", "pulse", "flags"])
  for i in range(0, n):
    # slice of the current answer from the big data blob
    d = ans[(data_offset + i * data_entry_len):(data_offset + (i+1) * data_entry_len)]

    # now split the data line into items
    user  = d[0]
    idx   = d[1]
    nl    = d[2]
    sys   = d[3]
    nl    = d[4]
    dia   = d[5]
    flags = d[6] # herzrythmus
    pulse = d[7]
    month = d[8]
    day   = d[9]
    year  = d[10] * 256 + d[11]
    hour  = d[12]
    minute= d[13]

    csvwriter.writerow([user, year, month, hour, minute, sys, dia, pulse, flags])
    print ("user=%d, %02d.%02d.%02d %02d:%02d sys=%03d, dia=%03d, pulse=%03d, flags=%d" %(user, day, month, year, hour, minute, sys, dia, pulse, flags))

