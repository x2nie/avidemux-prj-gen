import os
from datetime import timedelta
from lxml import etree

# FILM_PRJ = 'intro.wfp'
FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-6-APRIL\report-3-dimensi.wfp'
FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-6-APRIL\report-4-dimensi.wfp'
FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-6-APRIL\report-4d-fill-db.wfp'
# FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-APRIL-5\report-sederhana.wfp'
# FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-APRIL-5\report-bertumpuk.wfp'
FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-08-APRIL\no_4.wfp'
FILM_PRJ = r'C:\Users\citra\Videos\Logitech\LogiCapture\FINAL-08-APRIL\102-create-geo-entities-db.wfp'
# FILM_PRJ = r'WSVEFolder\Project\project.xml'

FILM_PRJ = os.path.abspath(FILM_PRJ) 
# FILM_BCPF = os.path.splitext(FILM_PRJ)[0] + '.bcpf'
FILM_MP4 = os.path.splitext(FILM_PRJ)[0] + '-py.mp4'

print(locals())

LOADED_VIDEO = []
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
        
from moviepy.editor import *
# ALL VIDEOS FIRST================================
LOADED_VIDEO =[] #reset
MP4s = {}
for m in META:
    source =  m['source']
    if not source in LOADED_VIDEO:        
        LOADED_VIDEO.append(source)
        MP4s[source] = VideoFileClip(source) # load from file

# <Property key="time.trim.start" type="NLERational" value="[1674, 25]: 66.9600000 "/>
def sfloat2timedelta(s):
    '66.9600000 to 66 960 000' #[1674, 25]: 66.9600000
    # <Property key="time.trim.start" type="NLERational" value="[1674, 25]: 66.9600000 "/>
    (dec,fric) = s.strip().split('.')
    fric = fric[:3]
    # fric = fric.ljust(3,'0')
    # print( fric )
    return timedelta(seconds=int(dec), microseconds=int(fric))


# ALL SEGMENT THEN================================
# LINES.append('adm.clearSegments()')
VIDEOS = []
duration = 0
total = timedelta(seconds=0)
for i, m in enumerate(META):
    source = m['source']
    src_idx= LOADED_VIDEO.index(source)
    level  = m['level']
    enable = '' if m['enable'] == '1' else '# '
    time   = m['time']
    pos0   = sfloat2timedelta(time['time.position.start'])
    posz   = sfloat2timedelta(time['time.position.end'])
    trim0  = sfloat2timedelta(time['time.trim.start'])
    duration = posz - pos0
    total += duration
    start  = str(trim0)
    end    = str(trim0 + duration)
    print( start, end)
    mp4 = MP4s.get(source)
    clip = mp4.subclip(start, end)
    VIDEOS.append(clip)
    

print('marker.end=', str(total))    
final_clip = concatenate_videoclips(VIDEOS)
final_clip.write_videofile(FILM_MP4, fps=24)



# with open(FILM_BCPF, 'w') as f:
#     f.write('\n'.join(LINES))
    