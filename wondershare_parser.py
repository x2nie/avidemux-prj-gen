from lxml import etree

FILM_PRJ = 'intro.wfp'

LOADED_VIDEO = []
LINES = [ # to be file.py lines
         '#PY  <- Needed to identify #',
         '#--automatically built--',
         '',
         'adm = Avidemux()',
]
META = [] # array of dict per segment



def read_film():
    # with open('project.xml') as f:
    #     tree = etree.parse(f)
    # root = etree.Element("TimeLine")
    # with open('project6.xml') as f:
    with open('intro.xml') as f:
        s = f.read()    
        return etree.XML(s)
    
root = read_film()    


print('@#root: ',root.tag)

# for child in root:
#     print(child.tag)
    
# print([x for x in root.findall(".//TimeLine")]) # lxml.etree only!    
for x in root.findall(".//TimeLine"):
    # print( etree.tostring(x))
    # <Property key="Render.Position" type="int" value="1553"/>
    # <Property key="Render.RangeFrameNumber" type="NLERange" value="Start:1818, End:2063"/>
    # <Property key="Render.RationPosition" type="NLERational" value="[1553, 1]: 1553.0000000 "/>

    # for y in x.findall(".//Property[@key='Render.*']"):
    # for y in x.findall('.//Property[starts-with(@key, "Render*")]'):
    # print( etree.tostring(x)[:500] )
    # for y in x.findall('''.//Property[@key='Render*']'''):
    
    
    # print( x.find('''.//Property[@key='Absolute.FilePath']''') )
    # print( x.xpath('''.//Property[@key='Absolute.FilePath']/@value''')[0] )
    source =  x.xpath('''.//Property[@key='Absolute.FilePath']/@value''')[0]
    # if source in LOADED_VIDEO:
    #     src_idx = LOADED_VIDEO.index(source)
    #     if len(LOADED_VIDEO) == 0:
    #         LINES.append('adm.loadVideo("%s")' % source)
    #     else:
    #         LINES.append('adm.appendVideo("%s")' % source)
    # else:
    #     LOADED_VIDEO.append(source)
    #     src_idx = LOADED_VIDEO.index(source)
        
    level =  x.xpath('''.//Property[@key='Level']/@value''')[0] #row of video|audio ;int
    
    enable =  x.xpath('''.//Property[@key='base.Enable']/@value''')[0] # mute=='0', normal='1' ;int
    
    
    
    time={}
    # for y in x.xpath(r'''.//Property[re:match(@key,'(time\.(position\.(end|start)|trim\.start)|Render\.(Position|RangeFrameNumber|RationPosition))')]''', namespaces={'re': 'http://exslt.org/regular-expressions'}):
    for y in x.xpath(r'''.//Property[re:match(@key,'time\.(position\.(end|start)|trim\.start)')]''', namespaces={'re': 'http://exslt.org/regular-expressions'}):
        # print( y.get('key'))
        key =  y.get('key')
        value = y.get('value').split(':')[-1].strip()
        print(key, value)
        time[key] = value
        # print( ' - ',etree.tostring(y) )
    # print(dir(y))
    META.append(dict(source=source, enable=enable, level=level, time=time))
    print()
        
# ALL VIDEOS FIRST================================
for m in META:
    source =  m['source']
    if not source in LOADED_VIDEO:        
        if len(LOADED_VIDEO) == 0:
            LINES.append('adm.loadVideo("%s")' % source)
        else:
            LINES.append('adm.appendVideo("%s")' % source)
        LOADED_VIDEO.append(source)

# ALL SEGMENT THEN================================
LINES.append('adm.clearSegments()')
total = 0
for m in META:
    source = m['source']
    src_idx= LOADED_VIDEO.index(source)
    level  = m['level']
    enable = '' if m['enable'] == '1' else '# '
    time   = m['time']
    pos0   = int(float(time['time.position.start']) * 1000000)
    posz   = int(float(time['time.position.end']) * 1000000)
    trim0  = int(float(time['time.trim.start']) * 1000000)
    duration = posz - pos0
    total += duration
    LINES.append('%sadm.addSegment(%s, %s, %s)' % (enable, src_idx, trim0, duration))

LINES += [    
'adm.markerA = 0',
'adm.markerB = %s' % total,
'adm.setPostProc(3, 3, 0)',
'adm.videoCodec("Copy")',
'adm.audioClearTracks()',
'adm.setSourceTrackLanguage(0,"und")',
'adm.audioAddTrack(0)',
'adm.audioCodec(0, "copy");',
'adm.audioSetDrc(0, 0)',
'adm.audioSetShift(0, 0, 0)',
'adm.setContainer("MP4", "muxerType=0", "optimize=1", "forceAspectRatio=False", "aspectRatio=1", "rotation=0")',
]

with open('generated_avidemux_prj.py', 'w') as f:
    f.write('\n'.join(LINES))
    
for l in LINES:
    print(l)    