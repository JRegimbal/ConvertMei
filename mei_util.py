import xml.etree.ElementTree as ElementTree

ElementTree.register_namespace('xml', 'http://www.w3.org/XML/1998/namespace')
ElementTree.register_namespace('', 'http://www.music-encoding.org/ns/mei')

def staff_based_to_sb(original_file, modified_file):
    mei_tree = ElementTree.parse(original_file)
    mei_tag = mei_tree.getroot()

    for section in mei_tag.findall('.//{http://www.music-encoding.org/ns/mei}section'):
        # Make staff and layer to be containers
        new_staff = ElementTree.Element('{http://www.music-encoding.org/ns/mei}staff', {'n': '1'})
        container = ElementTree.SubElement(new_staff, '{http://www.music-encoding.org/ns/mei}layer')
        container.set('n', '1')

        for staff in section:
            for layer in staff:
                # Replace every staff + layer with a system begin with the same facsimile
                sb = ElementTree.Element('{http://www.music-encoding.org/ns/mei}sb', {})
                sb.set('{http://www.w3.org/XML/1998/namespace}id', staff.get('{http://www.w3.org/XML/1998/namespace}id'))
                sb.set('facs', staff.get('facs'))
                # Check for custos
                if len(container) > 1:
                    if container[-1].tag == '{http://www.music-encoding.org/ns/mei}custos':
                        sb.append(container[-1])
                        container.remove(container[-1])
                    else:
                        print(container[-1].tag)

                # Check if first syllable has @follows
                first_syllable = layer.find('{http://www.music-encoding.org/ns/mei}syllable')
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
                    syllable = container.find('.//*[@{http://www.w3.org/XML/1998/namespace}id=\'' + syllable_id + '\']')
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
                count = 1   # Sets the 'n' attribute for the staves
                new_staff = ElementTree.Element('{http://www.music-encoding.org/ns/mei}staff', {'n': str(count)})
                count += 1
                container = None

                for elem in layer:
                    if elem.tag == '{http://www.music-encoding.org/ns/mei}sb':
                        if container is not None:
                            if len(list(container)) > 0:
                                if len(list(elem)) > 0:
                                    # Move custos
                                    container.extend(list(elem))
                                # Add our staff to the list
                                staff_store.append(new_staff)
                                new_staff = ElementTree.Element('{http://www.music-encoding.org/ns/mei}staff', {'n': str(count)})
                                count += 1
                        # Make sure new_staff uses the sb facs
                        new_staff.set('facs', elem.get('facs'))
                        new_staff.set('{http://www.w3.org/XML/1998/namespace}id', elem.get('{http://www.w3.org/XML/1998/namespace}id'))
                        container = ElementTree.SubElement(new_staff, '{http://www.music-encoding.org/ns/mei}layer')
                        container.set('n', '1')
                    else:
                        container.append(elem)
                if len(list(container)) > 0:
                    # Append the last staff if one exists
                    staff_store.append(new_staff)

        section_id = section.get('{http://www.w3.org/XML/1998/namespace}id')
        section.clear()
        section.set('{http://www.w3.org/XML/1998/namespace}id', section_id)
        section.extend(staff_store)

    mei_tree.write(modified_file, encoding='utf-8', xml_declaration=True)
