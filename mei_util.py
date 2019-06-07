from xml.etree import ElementTree

ElementTree.register_namespace('xml', 'http://www.w3.org/XML/1998/namespace')
ElementTree.register_namespace('', 'http://www.music-encoding.org/ns/mei')


def staff_based_to_sb(original_file, modified_file):
    mei_tree = ElementTree.parse(original_file)
    mei_tag = mei_tree.getroot()

    for section in mei_tag.findall('.//{http://www.music-encoding.org/ns/mei}section'):
        # Make staff and layer to be containers
        new_staff = ElementTree.Element(
            '{http://www.music-encoding.org/ns/mei}staff', {'n': '1'})
        container = ElementTree.SubElement(
            new_staff, '{http://www.music-encoding.org/ns/mei}layer')
        container.set('n', '1')

        for staff in section:
            for layer in staff:
                # Replace every staff + layer with a system begin with the same facsimile
                sb = ElementTree.Element('{http://www.music-encoding.org/ns/mei}sb', {
                    'n': staff.get('n'),
                    'facs': staff.get('facs'),
                    '{http://www.w3.org/XML/1998/namespace}id': staff.get('{http://www.w3.org/XML/1998/namespace}id')
                })

                # Check for custos
                if len(container) > 1:
                    if container[-1].tag == '{http://www.music-encoding.org/ns/mei}custos':
                        sb.append(container[-1])
                        container.remove(container[-1])
                    else:
                        print(container[-1].tag)

                # Check if first syllable has @follows
                first_syllable = layer.find(
                    '{http://www.music-encoding.org/ns/mei}syllable')
                syllable_id = ''
                if first_syllable is not None:
                    if first_syllable.get('follows') is not None:
                        print("follows is " + first_syllable.get('follows'))
                        syllable_id = first_syllable.get('follows')
                        # Remove syl tag(s), if any
                        for syl in first_syllable.findall('{http://www.music-encoding.org/ns/mei}syl'):
                            first_syllable.remove(syl)
                        layer.remove(first_syllable)
                    else:
                        first_syllable = None

                if first_syllable is None:
                    container.append(sb)
                else:
                    print("Non none first_syllable")
                    syllable = container.find(
                        './/*[@{http://www.w3.org/XML/1998/namespace}id=\'' + syllable_id + '\']')
                    syllable.append(sb)
                    syllable.extend(list(first_syllable))
                container.extend(list(layer))

        section_id = section.get('{http://www.w3.org/XML/1998/namespace}id')
        section.clear()
        section.set('{http://www.w3.org/XML/1998/namespace}id', section_id)
        section.append(new_staff)

    mei_tree.write(modified_file, encoding='utf-8', xml_declaration=True)


def sb_based_to_staff(original_file, modified_file):
    mei_tree = ElementTree.parse(original_file)
    mei_tag = mei_tree.getroot()

    for section in mei_tag.findall('.//{http://www.music-encoding.org/ns/mei}section'):
        # There should only be one staff, but iterating just to be safe
        staff_store = []
        for staff in section:
            for layer in staff:
                sb_indexes = [list(layer).index(sb) for sb in layer.findall(
                    '{http://www.music-encoding.org/ns/mei}sb')]
                for (sb_index, n) in zip(sb_indexes, range(0, len(sb_indexes))):
                    sb = layer[sb_index]

                    new_staff = ElementTree.Element(
                        '{http://www.music-encoding.org/ns/mei}staff', sb.attrib)
                    container = ElementTree.SubElement(
                        new_staff, '{http://www.music-encoding.org/ns/mei}layer')

                    # Check for custos
                    for custos in sb:
                        staff_store[-1][-1].append(custos)

                    # Set attributes
                    container.set('n', '1')

                    # Get elements to add
                    last_index = len(layer) if n + \
                        1 == len(sb_indexes) else sb_indexes[n + 1]
                    container.extend(layer[sb_index + 1:last_index])

                    staff_store.append(new_staff)

        section_id = section.get('{http://www.w3.org/XML/1998/namespace}id')
        section.clear()
        section.set('{http://www.w3.org/XML/1998/namespace}id', section_id)
        section.extend(staff_store)

        # Handle sb in syllables
        staves_added = 0
        for (staff, staff_index) in zip(section, range(0, len(section))):
            for layer in staff:
                for syllable in layer.findall('.//{http://www.music-encoding.org/ns/mei}syllable'):
                    sb = syllable.find(
                        '{http://www.music-encoding.org/ns/mei}sb')
                    if sb is None:
                        continue
                    new_staff = ElementTree.Element(
                        '{http://www.music-encoding.org/ns/mei}staff', sb.attrib)
                    new_layer = ElementTree.SubElement(
                        new_staff, '{http://www.music-encoding.org/ns/mei}layer')
                    new_layer.set('n', '1')

                    new_syllable = ElementTree.SubElement(
                        new_layer, '{http://www.music-encoding.org/ns/mei}syllable')
                    new_syllable.set('follows', syllable.get(
                        '{http://www.w3.org/XML/1998/namespace}id'))
                    new_syllable.extend(syllable[list(syllable).index(sb)+1:])

                    old_syllable_content = syllable[:list(syllable).index(sb)]
                    syllable_attrib = syllable.attrib

                    # Handle custos
                    layer.extend(list(sb))

                    # Shrink syllable
                    syllable.clear()
                    syllable.attrib = syllable_attrib
                    syllable.extend(old_syllable_content)

                    section.insert(staff_index + staves_added + 1, new_staff)

    mei_tree.write(modified_file, encoding='utf-8', xml_declaration=True)
