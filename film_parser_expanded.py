import os
import re
from lxml import etree

# FILM_PRJ = 'intro.wfp'
FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-6-APRIL\report-3-dimensi.wfp'
FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-6-APRIL\report-4-dimensi.wfp'
FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-6-APRIL\report-4d-fill-db.wfp'
FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-APRIL-5\report-sederhana.wfp'
FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-APRIL-5\report-bertumpuk.wfp'
FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-APRIL-5\combine-entities.wfp'
FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-APRIL-5\geo-entities-combined.wfp'

FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-08-APRIL\101-geo-entity-table-design-SINGKAT.wfp'
FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-08-APRIL\102-create-geo-entities-db.wfp'
# FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-08-APRIL\103-fill-negara.wfp'
FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-08-APRIL\no_4.wfp'
# FILM_PRJ = r'WSVEFolder\Project\project.xml'

FILM_PRJ = os.path.abspath(FILM_PRJ) 
FILM_PY = os.path.splitext(FILM_PRJ)[0] + '.py'
FILM_MP4 = os.path.splitext(FILM_PRJ)[0] + '.mp4'

print(locals())

LOADED_VIDEO = []
HEADER = [ # to be file.py lines
         '#PY  <- Needed to identify #',
         '#--automatically built--',
         '',
         'adm = Avidemux()',
]
FOOTER = ['adm.setPostProc(3, 3, 0)',
'adm.videoCodec("Copy")',
'adm.audioClearTracks()',
'adm.setSourceTrackLanguage(0,"und")',
'adm.audioAddTrack(0)',
'adm.audioCodec(0, "copy");',
'adm.audioSetDrc(0, 0)',
'adm.audioSetShift(0, 0, 0)',
'adm.setContainer("MP4", "muxerType=0", "optimize=1", "forceAspectRatio=False", "aspectRatio=1", "rotation=0")',
]
LINES = HEADER[:] #COPY 

META = [] # array of dict per segment



def read_film():
    if FILM_PRJ.endswith('.wfp'):
        from zipfile import ZipFile
        with ZipFile(FILM_PRJ) as myzip:
            with myzip.open('WSVEFolder/Project/project.xml') as myfile:
                s = myfile.read()
    else:
        with open(FILM_PRJ) as f:
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
    if not source in LOADED_VIDEO:        
        LOADED_VIDEO.append(source)
    # if source in LOADED_VIDEO:
    #     src_idx = LOADED_VIDEO.index(source)
    #     if len(LOADED_VIDEO) == 0:
    #         LINES.append('adm.loadVideo("%s")' % source)
    #     else:
    #         LINES.append('adm.appendVideo("%s")' % source)
    # else:
    #     LOADED_VIDEO.append(source)
    #     src_idx = LOADED_VIDEO.index(source)
    src_idx = LOADED_VIDEO.index(source)
        
    level =  x.xpath('''.//Property[@key='Level']/@value''')[0] #row of video|audio ;int
    
    enable =  x.xpath('''.//Property[@key='base.Enable']/@value''')[0] # mute=='0', normal='1' ;int
    
    
    
    time={}
    # for y in x.xpath(r'''.//Property[re:match(@key,'(time\.(position\.(end|start)|trim\.start)|Render\.(Position|RangeFrameNumber|RationPosition))')]''', namespaces={'re': 'http://exslt.org/regular-expressions'}):
    for y in x.xpath(r'''.//Property[re:match(@key,'time\.(position\.(end|start)|trim\.start)')]''', namespaces={'re': 'http://exslt.org/regular-expressions'}):
        # print( y.get('key'))
        key =  y.get('key')
        value = y.get('value').split(':')[-1].strip()
        print(src_idx, key, value, '|', y.get('value') )
        time[key] = value
        # print( ' - ',etree.tostring(y) )
    # print(dir(y))
    META.append(dict(source=source, enable=enable, level=level, time=time))
    print()
        
# ALL VIDEOS FIRST================================
LOADED_VIDEO =[] #reset
for m in META:
    source =  m['source']
    if not source in LOADED_VIDEO:        
        if len(LOADED_VIDEO) == 0:
            LINES.append('adm.loadVideo("%s")' % source)
        else:
            LINES.append('adm.appendVideo("%s")' % source)
        LOADED_VIDEO.append(source)


    
    
# <Property key="time.trim.start" type="NLERational" value="[1674, 25]: 66.9600000 "/>
def fixInt(s):
    '66.9600000 to 66 960 000' #[1674, 25]: 66.9600000
    # <Property key="time.trim.start" type="NLERational" value="[1674, 25]: 66.9600000 "/>
    (dec,fric) = s.strip().split('.')
    fric = fric[:6]
    fric = fric.ljust(6,'0')
    # print( fric )
    return int(dec+fric)

# ALL SEGMENT THEN================================
LINES.append('adm.clearSegments()')
duration = 0
total = 0
for m in META:
    source = m['source']
    src_idx= LOADED_VIDEO.index(source)
    level  = m['level']
    enable = '' if m['enable'] == '1' else '# '
    time   = m['time']
    pos0   = fixInt(time['time.position.start'])
    posz   = fixInt(time['time.position.end'])
    trim0  = fixInt(time['time.trim.start'])
    duration = posz - pos0
    m['START'] = trim0
    m['DURATION'] = duration
    total += duration
    LINES.append('%sadm.addSegment(%s, %s, %s)' % (enable, src_idx, trim0, duration))

LINES += [    
'adm.markerA = 0',
'adm.markerB = %s' % total,
] + FOOTER

with open(FILM_PY, 'w') as f:
    f.write('\n'.join(LINES))
    
# for l in LINES:
#     print(l)    


# [TimeToFrame] 03:29:10-407 We reached frame 21042 with a PTS of 842217968 when looking for PTS 842200000
# [ADM_EditorSegment::dtsFromPts] 03:29:10-407 Cannot get frame with pts=842200 ms
def fixUpWorseTimeline(admlog):
    regex = re.compile( r"(\d+) when looking for PTS (\d+)" )
    PTS={}
    FOUNDS = []
    for l in admlog:
        # print `l`
        if l.startswith('[TimeToFrame]'):
            match = regex.search(l)
            found = match.group(1)
            lookFor = match.group(2)
            if found in FOUNDS:
                break
            else:
                FOUNDS.append(found)
                PTS[int(lookFor)] = found
                
            print('MAT:', found)
    if not FOUNDS:
        return
    # ===============================================================================
    LINES = HEADER[:] #COPY
    # ALL VIDEOS FIRST================================
    LOADED_VIDEO =[] #reset
    for m in META:
        source =  m['source']
        if not source in LOADED_VIDEO:        
            if len(LOADED_VIDEO) == 0:
                LINES.append('adm.loadVideo("%s")' % source)
            else:
                LINES.append('adm.appendVideo("%s")' % source)
            LOADED_VIDEO.append(source)
        
    LINES.append('adm.clearSegments()')
    total = 0    
        
    for m in META:
        source = m['source']
        src_idx= LOADED_VIDEO.index(source)
        # level  = m['level']
        enable = '' if m['enable'] == '1' else '# '
        # time   = m['time']
        # pos0   = fixInt(time['time.position.start'])
        # posz   = fixInt(time['time.position.end'])
        # trim0  = fixInt(time['time.trim.start'])
        # duration = posz - pos0
        trim0 = m['START']
        if trim0 in PTS:
            trim0 = PTS[trim0]
        duration = m['DURATION'] 
        total += duration
        LINES.append('%sadm.addSegment(%s, %s, %s)' % (enable, src_idx, trim0, duration))

    LINES += [    
    'adm.markerA = 0',
    'adm.markerB = %s' % total,
    ] + FOOTER
    
    with open(FILM_PY, 'w') as f:
        f.write('\n'.join(LINES))
        
# import subprocess
# cmd = [
#     r'"D:\Program Files\Avidemux 2.7 VC++ 64bits\avidemux.exe"',
#     # https://www.avidemux.org/admWiki/doku.php?id=using:command_line_usage
#     '--run', FILM_PY,
#     '--output-format', 'MP4'
# ]
# # subprocess.run(cmd)
# subprocess.call(cmd)

import subprocess
# avidemux_file_conversion_command = 'avidemux_cli --nogui --output-format mp4 --run "' + FILM_PY  + '" --save "' + FILM_MP4 + '" --quit'
avidemux_file_conversion_command = 'avidemux_cli --nogui --output-format mp4 --run "' + FILM_PY  + '" --quit'
# avidemux_file_conversion_command = 'avidemux2_cli --nogui --audio-codec mp3 --video-codec x264 --output-format mp4 --load "' + video_file  + '" --save "' + new_video_file_name + '" --quit'
# subprocess.Popen(avidemux_file_conversion_command, shell=True)
out = subprocess.check_output(avidemux_file_conversion_command)
out = out.decode('utf-8')
print( out[-17500:])
print('back to py, outtyupe=', type(out))
out = out.split('\r\n')
out.reverse()
# print( out[:10])
fixUpWorseTimeline(out)


avidemux_file_conversion_command = 'avidemux_cli --nogui --output-format mp4 --run "' + FILM_PY  + '" --save "' + FILM_MP4 + '" --quit'
subprocess.Popen(avidemux_file_conversion_command, shell=True)
# avidemux_file_conversion_command = 'avidemux_cli --nogui --output-format mp4 --run "' + FILM_PY  + '" --quit'
# avidemux_file_conversion_command = 'avidemux2_cli --nogui --audio-codec mp3 --video-codec x264 --output-format mp4 --load "' + video_file  + '" --save "' + new_video_file_name + '" --quit'
