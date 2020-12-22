from lxml import etree as ET

import line_parser

# LINES = '10 minuten 40 -80%\n 1 Minute 110% \n 3 Minuten 60 % \n3x {\n3x { 10 Sekunden 200%\n 1:50 100%\n 2 Minuten 40%}\n 7 Minuten 40%}\n5 Minuten 40-20%'.splitlines()
LINES = '10 minuten 40 -80%\n 1 Minute 110% \n 3 Minuten 60 % \n3x (\n3x ( 3 Minuten 100%\n 3 Minuten 80% )\n 5 Minuten 40%)\n5 Minuten 40-20%'.splitlines()


class Parser:    # Just a facade
    def __init__(self):
        self.overall_seconds = 0

    def to_xml(self, inp, author='R. Espize', workout_name='Test-Workout', workout_description='Beschreibung mit einem\nZeilenumbruch'):
        self.overall_seconds = 0

        def append_to_workout(line_list, mult=1):
            if mult > 1 and len(line_list) == 2 and line_list[0][0] == line_parser.INTERVAL and line_list[1][0] == line_parser.INTERVAL:
                # here we know that we can use a IntervalsT element
                on_duration = line_list[0][1]
                off_duration = line_list[1][1]

                interval_el = ET.SubElement(workout_el, 'IntervalsT')
                interval_el.set('Repeat', str(mult))
                interval_el.set('OnDuration', str(on_duration))
                interval_el.set('OffDuration', str(off_duration))
                interval_el.set('OnPower', str(line_list[0][2]))
                interval_el.set('OffPower', str(line_list[1][2]))
                interval_el.set('pace', '0')

                self.overall_seconds += mult * (on_duration + off_duration)
            else:
                for _ in range(mult):
                    for i, l in enumerate(line_list):
                        line_type = l[0]
                        if line_type == line_parser.MULTIPLIER:
                            append_to_workout(l[2], mult=l[1])
                        elif line_type == line_parser.INTERVAL:
                            interval_el = ET.SubElement(workout_el, 'SteadyState')
                            interval_el.set('Duration', str(l[1]))
                            interval_el.set('Power', str(l[2]))
                            interval_el.set('pace', '0')

                            self.overall_seconds += l[1]
                        elif line_type == line_parser.COOLDOWN_WARMUP:
                            power1 = l[2]
                            power2 = l[3]
                            if power1 < power2:
                                # warmup
                                interval_el = ET.SubElement(workout_el, 'Warmup')
                            else:
                                interval_el = ET.SubElement(workout_el, 'Cooldown')
                            interval_el.set('Duration', str(l[1]))
                            interval_el.set('PowerLow', str(power1))
                            interval_el.set('PowerHigh', str(power2))
                            interval_el.set('pace', '0')

                            self.overall_seconds += l[1]

        file_el = ET.Element('workout_file')
        author_el = ET.SubElement(file_el, 'author')
        author_el.text = author
        name_el = ET.SubElement(file_el, 'name')
        name_el.text = workout_name
        description_el = ET.SubElement(file_el, 'description')
        description_el.text = workout_description
        type_el = ET.SubElement(file_el, 'sportType')
        type_el.text = 'bike'
        tags_el = ET.SubElement(file_el, 'tags')

        workout_el = ET.SubElement(file_el, 'workout')

        append_to_workout(inp)

        return file_el, self.overall_seconds


def to_xml(inp, author='R. Espize', workout_name='Test-Workout', workout_description='Beschreibung mit einem\nZeilenumbruch'):
    p = Parser()
    file_el, overall_seconds = p.to_xml(inp, author, workout_name, workout_description)
    return file_el, overall_seconds


def xml_to_file(xml_el, filename):
    str_data = ET.tostring(xml_el, pretty_print=True)
    with open(filename, "wb") as f:
        f.write(str_data)


def get_name_and_description_from_xml(file_path):
    tree = ET.parse(str(file_path))
    root = tree.getroot()
    name = root.find('name').text
    description = root.find('description').text
    return name, description


if __name__ == '__main__':
    # create a new XML file with the results
    parsed_lines = line_parser.parse_lines(LINES)
    xml_data, workout_duration = to_xml(parsed_lines)
    xml_to_file(xml_data, "test.xml")
