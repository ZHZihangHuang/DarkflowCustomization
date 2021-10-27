import os
import json
import pprint
import re

pp = pprint.PrettyPrinter(indent=4)
attempt_to_parse = input('Please enter which attempt instances to parse.')
# download instances_default.json from CVAT
instances_path = '%s/instances_default.json' % attempt_to_parse
with open(instances_path) as f:
  data = json.load(f)

# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}
for json_key in data:
    print(json_key)

# pp.pprint(data['annotations'])
with open('current_highest_id.txt', 'r') as f:
    content = f.readlines()
current_highest_id = int(content[0])

all_frame_xml = {}
for ann in data['annotations']:
    image_file_name = None
    image_width = None
    image_height = None
    for image in data['images']:
        if image['id'] != ann['image_id']:
            continue
        image_id = image['id']
        image_file_name = image['file_name']
        image_height = image['height']
        image_width = image['width']
        print('--------------------- Now parsing %s...' % image_file_name)
        print('image_id: %s' % image['id'])
        print('image_file_name: %s' % image['file_name'])
        print('image_height: %s' % image['height'])
        print('image_width: %s' % image['width'])

    print('ann_id: %s' % ann['id'])
    print('ann_image_id: %s' % ann['image_id'])
    print('ann_bbox_id: %s' % ann['bbox'])
    xmin = ann['bbox'][0]
    ymin = ann['bbox'][1]
    xdelta = ann['bbox'][2]
    ydelta = ann['bbox'][3]
    category_name = None
    for category in data['categories']:
        if category['id'] != ann['category_id']:
            continue
        category_name = category['name']
        print('category_name: %s' % category['name'])
        print('category_id: %s' % category['id'])

    frame_xml = """	<filename>%s</filename>
    <size>
        <width>%s</width>
        <height>%s</height>
        <depth>3</depth>
    </size>
    <segmented>0</segmented>\n""" % (image_file_name, image_width, image_height)
    objs = """    <object>
        <name>%s</name>
        <pose>Left</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>%s</xmin>
            <ymin>%s</ymin>
            <xmax>%s</xmax>
            <ymax>%s</ymax>
        </bndbox>
    </object>\n""" % (category_name, round(xmin), round(ymin), round(xmin+xdelta), round(ymin+ydelta))
    print(frame_xml)
    print(xmin, ymin, xmin+xdelta, ymin+ydelta)
    frame_number_match = re.search('frame([0-9]+)\.xml', 'abcdef')
    if frame_number_match:
        frame_number = int(frame_number_match.group(1)) + current_highest_id
        print('frame_number_match.group(1): %s' % frame_number_match.group(1))
    else:
        frame_number = current_highest_id + 1
        print('frame_number: %s' % frame_number)
    current_highest_id = frame_number
    xml_path = 'xmls\\%s' % image_file_name.replace('.jpg', '.xml')
    if xml_path in all_frame_xml:
        all_frame_xml[xml_path][-1] += objs
    else:
        all_frame_xml[xml_path] = [frame_xml, objs]

outfile = open('current_highest_id.txt', 'w')
outfile.write(str(current_highest_id))
outfile.close()

for xml_path in all_frame_xml:
    outfile = open(xml_path, 'a')
    outfile.write('<annotation>\n')
    outfile.write(all_frame_xml[xml_path][0])
    outfile.write(all_frame_xml[xml_path][1])
    outfile.write('</annotation>\n')
    outfile.close()

