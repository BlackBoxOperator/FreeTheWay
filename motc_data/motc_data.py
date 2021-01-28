from __future__ import print_function
import logging, sys
import argparse
import wget
import os
import xmltodict
import xml.etree.ElementTree as ET
from collections import OrderedDict
from functools import partial

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def wget_from_url(url, name=None):
    name = url.rsplit('/', 1)[-1] if not name else name
    if os.path.exists(name):
      os.remove(name)
    wget.download(url, out=name)

def download(option):
  motc_prefix = 'https://tisvcloud.freeway.gov.tw/history/motc20/'
  if option == 'static' or option == 'all':
    [wget_from_url(motc_prefix + x) 
      for x in ['Section.xml',      # Basic information of road section
                'SectionShape.xml', # Map shape information of road section (wkt info)
                'SectionLink.xml',  # SectionID to LinkIDs information
                'ETag.xml'          # Etag information of LinkID
                ]]
                                              
  if option == 'dynamic' or option == 'all':
    [wget_from_url(motc_prefix + x) 
      for x in ['LiveTraffic.xml'   # Real-time traffic information on road section
                ]]

  else:
    eprint('invalid download option (dynamic/static/all)')

def extract_data(xml_file, callback=None):
  if not callback:
    eprint('The callback option is needed (a function to deal with the xml root)')
    sys.exit('Error on extract_data')

  tree = ET.parse(xml_file)
  root = tree.getroot()
  prefix = root.tag.split('}', 1)[0] + '}'
  return callback(root=root, prefix=prefix)
  
def shapes_process(root, prefix=''):
  Dict = {}
  for child in root.find(prefix + 'SectionShapes'):
    section_id = child.find(prefix + 'SectionID').text
    shape = child.find(prefix + 'Geometry').text
    
    logging.debug(f' SectionID: {section_id}, Shape: {shape}')
    
    Dict[section_id] = shape
  return Dict

def livetraffic_process(root, prefix=''):
  Dict = {}
  for child in root.find(prefix + 'LiveTraffics'):
    section_id = child.find(prefix + 'SectionID').text
    travel_time = child.find(prefix + 'TravelTime').text
    congestion_level = child.find(prefix + 'CongestionLevel').text
    travel_speed = child.find(prefix + 'TravelSpeed').text
    
    logging.debug(f' SectiondID: {section_id}, travel time: {travel_time}, congestion: {congestion_level}, travel speed: {travel_speed}')

    Dict[section_id] = {'TravelTime': travel_time, 'CongestionLevel': congestion_level, 'TravelSpeed': travel_speed}
  return Dict

def linkid_process(root, prefix=''):
  Dict = {}
  for child in root.find(prefix + 'SectionLinks'):
    sec_id = child.find(prefix + 'SectionID').text
    link_ids = child.find(prefix + 'LinkIDs')
    result = [l.text for l in link_ids.findall(prefix + 'LinkID')]
    
    logging.debug(f' SectionID: {sec_id}, linkIDs: {result}')
    
    Dict[sec_id] = result
  return Dict
    
def etag_process(root, prefix=''):
  Dict = {}
  for child in root.find(prefix + 'ETags'):
    etag_id = child.find(prefix + 'ETagGantryID').text
    link_id = child.find(prefix + 'LinkID').text
    road_id = child.find(prefix + 'RoadID').text

    logging.debug(f' Etag: {etag_id}, LinkID: {link_id}, RoadID: {road_id}')
    
    Dict [etag_id] = {'LinkID': link_id, 'RoadID': road_id}
  return Dict
  
# The default road for id_process is 國道 1 號 (000010)
def id_process(root, road='000010', prefix=''):
  Dict = {'N': OrderedDict(), 'S': OrderedDict()}
    
  for child in root.find(prefix + 'Sections'):
    road_id = child.find(prefix + 'RoadID').text
    
    # only the giving road will be processed
    if road_id != road:
      continue

    road_direction = child.find(prefix + 'RoadDirection').text
    section_id = child.find(prefix + 'SectionID').text
    _sec = child.find(prefix + 'RoadSection')
    start, end = _sec.find(prefix + 'Start').text, _sec.find(prefix + 'End').text
    sec_length = child.find(prefix + 'SectionLength').text

    logging.debug(f' SectionID: {section_id}, RoadID: {road_id}, ({start}, {end}), Length: {sec_length}')
    
    Dict[road_direction][section_id] = {'RoadID': road_id, 'Start': start, 'End': end, 'Length': sec_length}
  return Dict

# e.g. 台北交流道, 新竹交流道  
def traffic_of_two_points(start, end, section_ids):
  # e.g. section_ids = extract_data('Section.xml', callback=partial(id_process, road='000010'))
  ## Create an inverse table from section_ids
  last_elem = next(reversed(section_ids['S'].items()))

  inverse_table = OrderedDict([(value['Start'], (i, key)) for i, (key, value) in enumerate(section_ids['S'].items())] + \
                              [(last_elem[1]['End'], (len(section_ids['S']), last_elem[0]))])

  x1 = inverse_table[start]
  x2 = inverse_table[end]

  direction = ('S', 1) if x1[0] < x2[0] else ('N', -1)
  fix = 1 if direction[0] == 'N' else 0

  traffic = list(section_ids[direction[0]].items())[x1[0]-fix:x2[0]-(fix if x2[0] != 0 else 0):direction[1]] +\
            ([list(section_ids[direction[0]].items())[x2[0]]] if x2[0] == 0 else [])

  return traffic

  
def main():
  parser = argparse.ArgumentParser(description='MOTC extractor example')
  parser.add_argument('--download', type=str, default='none', metavar='N',
                      help='Download the data from MOTC (static/dynamic/all)')
  # parser.add_argument('--save-dict', action='store_true', default=False,
  #                       help='For Saving the current dict')
  parser.add_argument('--debug', action='store_true', default=False,
                        help='For Saving the current ')                        
  args = parser.parse_args()
  
  if not args.debug:
    logging.disable(logging.DEBUG)

  # Usage
  ## Download the data from motc (static / dynamic / all)
  ## dynamic: only the real-time information will be downloaded from MOTC
  ## static: the static information ...
  ## all: dynamic + static
  if args.download != 'none':
    download(args.download)

  ## Extract the Section IDs information on giving road (e.g. 國道 1 號: 000010) -> OrderedDict(key=section_id)
  section_ids = extract_data('Section.xml', callback=partial(id_process, road='000010'))

  ## Extract the Live Traffic information -> Dict(key=section_id)
  live_traffic = extract_data('LiveTraffic.xml', callback=livetraffic_process)

  ## Extract the Live Traffic information -> Dict
  shapes = extract_data('SectionShape.xml', callback=shapes_process)

  ## Extract the Mapping of SectionID to LinkID -> Dict
  section_links = extract_data('SectionLink.xml', callback=linkid_process)

  

  traffic = traffic_of_two_points('高雄端', '基隆端', section_ids)
  print(traffic)

  print('Travel Time: ', sum([int(live_traffic[key]['TravelTime']) for key, value in traffic]))

  

if __name__ == '__main__':
  main()
