import os, sys, ipaddress, csv, socket, struct, re, binascii, time, json

# Custom functions start at here
def no2ip(iplong):
    return (socket.inet_ntoa(struct.pack('!I', int(iplong))))

def ip2no(ip):
    return (struct.unpack("N",socket.inet_aton(ip)))

def myprint(d): 
    stack = list(d.items()) 
    visited = set() 
    while stack: 
        k, v = stack.pop() 
        if isinstance(v, dict): 
            if k not in visited: 
                stack.extend(v.items()) 
            else: 
                print("%s: %s" % (k, v)) 
            visited.add(k)

def travtree(hash, level, trace):
    leftval = -1
    rightval = -1
    leftleaf = 0
    rightleaf = 0
    for k, v in sorted(hash.items(), key=lambda x: random.random()):
        key2 = k
        trace2 = trace + key2
        if isinstance(v, str):
            if (k == 'x0'):
                leftval = v
                leftleaf = 1
            elif (k == 'x1'):
                rightval = v
                rightleaf = 1
        elif isinstance(v, dict):
            tmp = travtree(v, level + 1, trace2)
            if (k == 'x0'):
                leftval = tmp
            elif (k == 'x1'):
                rightval = tmp
    ownoffset = 0
    if (level in data):
        ownoffset = len(data[level])
    else:
        data[level] = {}
    
    data[level][ownoffset] = str(leftval) + '#' + str(rightval)
    return ownoffset

def custom_sprintf(num1):
    return format(int(num1), '08b')

def print_double(num):
    s = struct.pack(">d", float(num))
    return s

def print_byte(num):
    # s = struct.pack('B', int(num))
    s = struct.pack('I', int(num)).rstrip(b'\x00')
    return s

def print_byte1(num):
    s = struct.pack('B', int(num))
    return s

def print_uint(num):
    s = ""
    while (num > 0):
        num2 = int(num) & 0xFF 
        if (isinstance(s, bytes)):
            s = print_byte(num2) + s
        else:
            s = print_byte(num2) + bytes(s.encode())
        num = int(num) >> 8
    if (isinstance(s, bytes)):
        return s
    else:
        return bytes(s.encode())

def print_pointer(num):
    pointersize = -1
    threebits = 0
    balance = []

    if (num <= 2047):
        pointersize = 0
        threebits = num >> 8
        balance = get_byte_array(num, 1)
    elif(num <= 526335):
        pointersize = 1
        num = num - 2048
        threebits = num >> 16
        balance = get_byte_array(num, 2)
    elif(num <= 134744063):
        pointersize = 2
        num = num - 526336
        threebits = num >> 24
        balance = get_byte_array(num, 3)
    elif(num <= 4294967295):
        pointersize = 3
        threebits = 0
        balance = get_byte_array(num, 4)
    else:
        raise Exception("Pointer value too large.\n")

    pointersize = pointersize << 3
    controlbyte = pointertype | pointersize | threebits
    s = print_byte(controlbyte)
    for i in range(len(balance)):
        s += print_byte(balance[i])
    return s

def get_byte_array(num, bytes):
    bytesarr = []
    for i in range(bytes):
        tmp = int(num) & 0xFF
        num = int(num) >> 8
        bytesarr = ([tmp] + bytesarr) # do the unshift staff in Perl

    return bytesarr

def print_node (leftdata, rightdata): 
    mybytes = []
    leftbytes = []
    rightbytes = []
    
    if (dbtype == 'country'):
        leftbytes = get_byte_array(leftdata, 3)
        rightbytes = get_byte_array(rightdata, 3)
        mybytes = leftbytes + rightbytes
    elif (dbtype == 'city'):
        leftbytes = get_byte_array(leftdata, 4)
        rightbytes = get_byte_array(rightdata, 4)
        midbyte = (leftbytes[0] << 4) ^ rightbytes[0]
        leftbytes_a = leftbytes[0]
        leftbytes.pop(leftbytes.index(leftbytes_a))
        rightbytes_a = rightbytes[0]
        rightbytes.pop(rightbytes.index(rightbytes_a))
        leftbytes.append(midbyte)
        mybytes = leftbytes + rightbytes
    
    s = ""
    for i in range(len(mybytes)):
        if (isinstance(s, bytes)):
            s += print_byte1(mybytes[i])
        else:
            s = print_byte1(mybytes[i]) + bytes(s.encode())

    return s

def keys_exists(element, *keys):
    '''
    Check if *keys (nested) exists in `element` (dict).
    '''
    if not isinstance(element, dict):
        raise AttributeError('keys_exists() expects dict as first argument.')
    if len(keys) == 0:
        raise AttributeError('keys_exists() expects at least two arguments, one given.')

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except (KeyError, TypeError):
            return False
    return True

# Variables declaration start at here
tokens = {"country": 0, "iso_code": 0, "names": 0, "en": 0, "-": 0}
tokens2 = {"city": 0, "location": 0, "postal": 0, "latitude": 0, "longitude": 0, "code": 0, "subdivisions": 0}
latlongs = {}
cities = {}
countries = {}
cidrdata = []
sortbylength = {}
countryoffset = {}
cityoffset = {}
btree = {}
data = {}
datastartmarker = print_byte1(0) * 16
datastartmarkerlength = len(datastartmarker)

if (len(sys.argv) > 1):
    filename = sys.argv[1]
    if(filename.lower().endswith('.csv')):
        with open(filename, 'r', encoding = 'utf-8') as f:
            mycsv = csv.reader(f)
            for row in mycsv:
                therest = ''
                if (len(row) == 10):
                    dbtype = 'city'
                    for i in range (2,6):
                        tokens[row[i]] = 0
                    latlongs[row[6]] = 0
                    latlongs[row[7]] = 0
                    tokens[row[8]] = 0
                    cities[row[2] + "|" + row[3] + "|" + row[4] + "|" + row[5] + "|" + row[6] + "|" + row[7] + "|" + row[8]] = 0
                    therest = row[2] + "|" + row[4] + "|" + row[5] + "|" + row[6] + "|" + row[7] + "|" + row[8]
                else:
                    dbtype = 'country'
                    countries[row[2]] = row[3]
                    therest = row[2]
                fromip = no2ip(row[0])
                toip = no2ip(row[1])
                startip = ipaddress.IPv4Address(fromip)
                endip = ipaddress.IPv4Address(toip)
                ar = [ipaddr for ipaddr in ipaddress.summarize_address_range(startip, endip)]
                ar1 = []
                for i in range(len(ar)):
                    ar1.append(str(ar[i]))
                ar1 = sorted(ar1,key=lambda x : [int(m) for m in re.findall("\d+",x)])
                for i in range(len(ar1)):
                    cidrdata.append('"' + str(ar1[i]) + '",' + therest)
        for i in range(len(cidrdata)):
            regex_here1 = r"^\"([\d\.]+)\/(\d+)\",(.*)"
            if ((re.search(regex_here1, cidrdata[i]) != None)):
                matches = re.finditer(regex_here1, cidrdata[i], re.MULTILINE)
                for matchNum, match in enumerate(matches, start=1):
                    ip = match.group(1)
                    cidr = match.group(2)
                    line_copy1 = match.group(3)
                    iparr = ip.split('.')
                    binary = list(map(custom_sprintf, iparr))
                    binarystr = "".join(binary)
                    binarystrcidr = binarystr[0:int(cidr)]
                    sortbylength["GG" + binarystrcidr] = line_copy1
        datasection = b""
        stringtype = 2 << 5
        maptype = 7 << 5
        pointertype = 1 << 5
        uint16type = 5 << 5
        uint32type = 6 << 5
        uint64type = 9 - 7
        arraytype = 11 - 7
        extendedtype = 0
        doubletype = 3 << 5
        if (dbtype == 'city'):
            newHash = {**tokens, **tokens2} 
            tokens = newHash
        for key in sorted(tokens):
            tokens[key] = len(datasection)
            tokenlength = len(key)
            controlbyte = stringtype | tokenlength
            datasection += print_byte(controlbyte) + bytes(key.encode())
        for key1 in sorted(latlongs):
            # print (key1)
            latlongs[key1] = len(datasection)
            controlbyte1 = doubletype | 8
            datasection += print_byte(controlbyte1) + print_double(key1)
        if (dbtype == 'country'):
            for key2 in sorted(countries):
                countryoffset[key2] = len(datasection)
                
                controlbyte = maptype | 1
                datasection += print_byte(controlbyte)
                datasection += print_pointer(tokens["country"])
                
                controlbyte = maptype | 2
                datasection += print_byte(controlbyte)
                datasection += print_pointer(tokens["iso_code"])
                
                tokenlength = len(key2)
                controlbyte = stringtype | tokenlength
                datasection += print_byte(controlbyte) + bytes(key2.encode())
                datasection += print_pointer(tokens["names"])
                
                controlbyte = maptype | 1
                datasection += print_byte(controlbyte)
                datasection += print_pointer(tokens["en"])
                
                countryname = countries[key2]
                tokenlength = len(countryname)
                controlbyte = stringtype | tokenlength
                datasection += print_byte(controlbyte) + bytes(countryname.encode())
        elif (dbtype == 'city'):
            for key2 in sorted(cities):
                array = key2.split('|')
                countrycode = array[0]
                countryname = array[1]
                statename = array[2]
                cityname = array[3]
                latitude = array[4]
                longitude = array[5]
                postcode = array[6]
                cityoffset[countrycode + "|" + statename + "|" + cityname + "|" + latitude + "|" + longitude + "|" + postcode] = len(datasection)
                controlbyte = maptype | 5
                datasection += print_byte(controlbyte)
                datasection += print_pointer(tokens["city"])
                controlbyte = maptype | 1
                datasection += print_byte(controlbyte)
                datasection += print_pointer(tokens["names"])
                controlbyte = maptype | 1
                datasection += print_byte(controlbyte)
                datasection += print_pointer(tokens["en"])
                datasection += print_pointer(tokens[cityname])
                
                datasection += print_pointer(tokens["country"])
                controlbyte = maptype | 2
                datasection += print_byte(controlbyte)
                datasection += print_pointer(tokens["iso_code"])
                datasection += print_pointer(tokens[countrycode])
                datasection += print_pointer(tokens["names"])
                controlbyte = maptype | 1
                datasection += print_byte(controlbyte)
                datasection += print_pointer(tokens["en"])
                datasection += print_pointer(tokens[countryname])
                
                datasection += print_pointer(tokens["location"])
                controlbyte = maptype | 2
                datasection += print_byte(controlbyte)
                datasection += print_pointer(tokens["latitude"])
                datasection += print_pointer(latlongs[latitude])
                datasection += print_pointer(tokens["longitude"])
                datasection += print_pointer(latlongs[longitude])
                
                datasection += print_pointer(tokens["postal"])
                controlbyte = maptype | 1
                datasection += print_byte(controlbyte)
                datasection += print_pointer(tokens["code"])
                datasection += print_pointer(tokens[postcode])
                
                datasection += print_pointer(tokens["subdivisions"])
                myint = 1
                controlbyte = extendedtype | myint
                typebyte = arraytype
                datasection += print_byte(controlbyte) + print_byte(typebyte)
                controlbyte = maptype | 1
                datasection += print_byte(controlbyte)
                datasection += print_pointer(tokens["names"])
                controlbyte = maptype | 1
                datasection += print_byte(controlbyte)
                datasection += print_pointer(tokens["en"])
                datasection += print_pointer(tokens[statename])
        for binarystrcidr in sorted(sortbylength):
            tmp = binarystrcidr
            tmp_modify = re.sub('GG', '', tmp)
            myarr = list(tmp_modify)
            key1_tmp = ''
            key1_tmp1 = ''
            code = 'btree'
            code1 = 'btree'
            for i in range(len(myarr)):
                code += '["x' + myarr[i] + '"]'
                key1 = 'x' + myarr[i]
                key1_tmp2 = 'x' + myarr[i]
                key1_tmp += '["x' + myarr[i] + '"]'
                key1_tmp1_list = key1_tmp1.split(',')
                for j in range(len(key1_tmp1_list)):
                    if (key1_tmp1_list[j] != ''):
                        code1 += '[' + key1_tmp1_list[j] + ']'
                if (key1_tmp1 == ''):
                    key1_tmp1 += '"' + key1 + '"'
                else:
                    key1_tmp1 += ',"' + key1 + '"'
                code2 = 'result123 = keys_exists(btree, ' + key1_tmp1 + ')'
                exec(code2)
                if (result123 == False):
                    code1 += '.setdefault("x' + myarr[i] + '", {})'
                    exec (code1)
                    code1 = 'btree'
                else:
                    code1 = 'btree'
            code += ' = "' + sortbylength[binarystrcidr] + '"'
            exec (code)
            key1_tmp = ''
            key1_tmp1 = ''
        travtree(btree, 0, '')
        totalnodes = 0
        offsetnodes = {}
        for i in range(len(data)):
            nodes = len(data[i])
            totalnodes += nodes
            offsetnodes[i] = totalnodes
        # Start to write into file
        filename2 = filename + '.MMDB'
        f = open(filename2,'wb')
        for i in range(len(data)):
            datalevel = len(data[i])
            for y in range(datalevel):
                nodedata = data[i][y]
                regex = r"^(.*)\#(.*)$"
                if ((re.search(regex, nodedata) != None)):
                    matches = re.finditer(regex, nodedata, re.MULTILINE)
                    for matchNum, match in enumerate(matches, start=1):
                        left = match.group(1)
                        right = match.group(2)
                        leftdata = 0
                        rightdata = 0
                        if (re.search(r"^\d+$", left) != None):
                            left_int = int(left)
                            left_int += offsetnodes[i]
                            leftdata = str(left_int)
                        else:
                            if (dbtype == 'country'):
                                if ((left.replace('-','',1).isdigit()) and (int(left) < 0)):
                                    leftdata = 0 + datastartmarkerlength + totalnodes
                                else:
                                    leftdata = countryoffset[left] + datastartmarkerlength + totalnodes
                            elif (dbtype == 'city'):
                                if ((left.replace('-','',1).isdigit()) and (int(left) < 0)):
                                    leftdata = 0 + datastartmarkerlength + totalnodes
                                else:
                                    leftdata = cityoffset[left] + datastartmarkerlength + totalnodes
                        if (re.search(r"^\d+$", right) != None):
                            right_int = int(right)
                            right_int += offsetnodes[i]
                            rightdata = str(right_int)
                        else:
                            if (dbtype == 'country'):
                                if ((right.replace('-','',1).isdigit()) and (int(right) < 0)):
                                    rightdata = 0 + datastartmarkerlength + totalnodes
                                else:
                                    rightdata = countryoffset[right] + datastartmarkerlength + totalnodes
                            elif (dbtype == 'city'):
                                if ((right.replace('-','',1).isdigit()) and (int(right) < 0)):
                                    rightdata = 0 + datastartmarkerlength + totalnodes
                                else:
                                    rightdata = cityoffset[right] + datastartmarkerlength + totalnodes
                    f.write(print_node(leftdata, rightdata))
        f.write(datastartmarker)
        f.write(datasection)
        f.write(binascii.unhexlify(b'ABCDEF4D61784D696E642E636F6D'))
        controlbyte = maptype | 9
        f.write(print_byte(controlbyte))
        field = "binary_format_major_version"
        fieldlength = len(field)
        controlbyte = stringtype | fieldlength
        f.write(print_byte(controlbyte) + bytes(field.encode()))
        myint = 2
        myint = print_uint(myint)
        intbytes = len(myint)
        controlbyte = uint16type | intbytes
        f.write(print_byte(controlbyte) + myint)
        field = "binary_format_minor_version"
        fieldlength = len(field)
        controlbyte = stringtype | fieldlength
        f.write(print_byte(controlbyte) + bytes(field.encode()))
        myint = 0
        myint = print_uint(myint)
        intbytes = len(myint)
        controlbyte = uint16type | intbytes
        f.write(print_byte(controlbyte) + myint)
        field = "build_epoch"
        fieldlength = len(field)
        controlbyte = stringtype | fieldlength
        f.write(print_byte(controlbyte) + bytes(field.encode()))
        myint = time.time()
        myint = print_uint(myint)
        intbytes = len(myint)
        controlbyte = extendedtype | intbytes
        typebyte = uint64type
        f.write(print_byte(controlbyte) + print_byte(typebyte) + myint)
        field = "database_type"
        fieldlength = len(field)
        controlbyte = stringtype | fieldlength
        f.write(print_byte(controlbyte) + bytes(field.encode()))
        if (dbtype == 'country'):
            field = "IP2LITE-Country"
        else:
            field = "IP2LITE-City"
        fieldlength = len(field)
        controlbyte = stringtype | fieldlength
        f.write(print_byte(controlbyte) + bytes(field.encode()))
        field = "description"
        fieldlength = len(field)
        controlbyte = stringtype | fieldlength
        f.write(print_byte(controlbyte) + bytes(field.encode()))
        controlbyte = maptype | 1
        f.write(print_byte(controlbyte))
        field = "en"
        fieldlength = len(field)
        controlbyte = stringtype | fieldlength
        f.write(print_byte(controlbyte) + bytes(field.encode()))
        if (dbtype == 'country'):
            field = "IP2LITE-Country database"
        else:
            field = "IP2LITE-City database"
        fieldlength = len(field)
        controlbyte = stringtype | fieldlength
        f.write(print_byte(controlbyte) + bytes(field.encode()))
        field = "ip_version"
        fieldlength = len(field)
        controlbyte = stringtype | fieldlength
        f.write(print_byte(controlbyte) + bytes(field.encode()))
        myint = 4
        myint = print_uint(myint)
        intbytes = len(myint)
        controlbyte = uint16type | intbytes
        f.write(print_byte(controlbyte) + myint)
        field = "languages"
        fieldlength = len(field)
        controlbyte = stringtype | fieldlength
        f.write(print_byte(controlbyte) + bytes(field.encode()))
        myint = 1
        controlbyte = extendedtype | myint
        typebyte = arraytype
        f.write(print_byte(controlbyte) + print_byte(typebyte))
        field = "en"
        fieldlength = len(field)
        controlbyte = stringtype | fieldlength
        f.write(print_byte(controlbyte) + bytes(field.encode()))
        field = "node_count"
        fieldlength = len(field)
        controlbyte = stringtype | fieldlength
        f.write(print_byte(controlbyte) + bytes(field.encode()))
        myint = totalnodes
        myint = print_uint(myint)
        intbytes = len(myint)
        controlbyte = uint32type | intbytes
        f.write(print_byte(controlbyte) + myint)
        field = "record_size"
        fieldlength = len(field)
        controlbyte = stringtype | fieldlength
        f.write(print_byte(controlbyte) + bytes(field.encode()))
        if (dbtype == 'country'):
            myint = 24
        else:
            myint = 28
        myint = print_uint(myint)
        intbytes = len(myint)
        controlbyte = uint32type | intbytes
        f.write(print_byte(controlbyte) + myint)
        f.close()
        print ("You have successfully converted",filename,"to",filename2,".\n")
        print ("You can now use the",filename2,"with any MaxMind API which supports the GeoLite2 format.\n")

    else:
        raise Exception('Only .csv file are accepted.')
else:
    print ("Usage: python3 convert.py <IP2Location LITE DB1 or DB11 CSV file>\n")
    raise Exception('Please enter a filename.')

