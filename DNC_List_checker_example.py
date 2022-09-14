import lxml.etree as ET
import csv, re, phonenumbers

#Files have to either be in the same folder as this script, or use absolute paths
incsv = 'contacts.csv'
outcsv     = 'out.csv'

xmlarray = ['your_DNC_file.xml',]

acArray = [None] * len(xmlarray);
for ix, xmlfile in enumerate(xmlarray):
    acArray[ix] = ET.parse(xmlfile).getroot().find('ac')
#print(acArray)

in_confile = open(incsv, "r", newline='', encoding='utf-8-sig')
reader = csv.DictReader(in_confile)
fields = reader.fieldnames;
#print(fields)
out_confile = open(outcsv, "w", newline='', encoding="utf-8-sig")
writer = csv.DictWriter(out_confile, fieldnames=fields)
writer.writeheader()

for row in reader:
    rawnum = row['Phone'] #Use your own header here
    if re.fullmatch('\d{10}', 
                    re.sub('[()-\. ]','',
                            re.sub('ext.*','',rawnum))):
        parsenum = phonenumbers.parse(rawnum,"US")
    elif re.match('\+', rawnum):
        parsenum = phonenumbers.parse(rawnum, None)
        #print(str(parsenum.country_code))
        #print(parsenum.national_number)
    elif rawnum == '':
        continue
    else:
        try:
            parsenum = phonenumbers.parse(rawnum, "US")
            #print(parsenum)
        except Exception as e:
            print(rawnum+' had an error being parsed: ')
            print(e)

    try: 
        #print('looking up '+rawnum)
        if parsenum.country_code == 1:
            natnum = str(parsenum.national_number)
            if len(natnum) == 10 :
                area = natnum[:3]
                number = natnum[3:]

                for ac in acArray:
                    if area == ac.get('val'):
                        dnc=ac.find("./ph[@val='{}']".format(str(number)))
                        print(area, number, str(dnc)) #, (dnc is not None))
                        if dnc is not None:
                            row['Do Not Call'] = 'Do Not Call';
                            #print(row)
                            writer.writerow(row)
                        elif dnc is None: 
                            row['Do Not Call'] = 'Okay';
                            writer.writerow(row)
                        break

    except Exception as e:
            print(rawnum+' had an error during lookup: ')
            print(e)
in_confile.close()
out_confile.close()