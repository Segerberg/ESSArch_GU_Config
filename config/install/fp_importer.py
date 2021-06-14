import django
django.setup()
import csv
import sys

from django.db import transaction

from ESSArch_Core.tags.models import Structure, StructureUnit, StructureType, StructureUnitType


@transaction.atomic
def import_fp(path):
    with open(path) as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        structure_type,_ = StructureType.objects.get_or_create(name='förteckningsplan')
        structure_name = reader.__next__()[0]
        structure = Structure.objects.create(name=structure_name, type=structure_type, is_template=True,
                                             published=True)

        reader.__next__()

        last_on_level = {}
        for row in reader:
            if not ''.join(row).strip():
                continue

            huvudavd, underavd, underavd2,underavd3, namn, beskrivning = row
            for idx, (col_name, col_val) in enumerate([('serie', huvudavd), ('serie', underavd), ('serie', underavd2), ('serie', underavd3)]):
                if col_val:
                    unit_type = StructureUnitType.objects.get_or_create(name= col_name, structure_type=structure_type)

                    reference_code = col_val
                    level = idx
                    break

            parent = None
            if level > 0:
                parent = last_on_level[level - 1]

            unit = StructureUnit.objects.create(structure=structure, parent=parent, type=unit_type[0], reference_code=reference_code, name=namn, description=beskrivning, comment="")
            last_on_level[level] = unit


if __name__ == '__main__':
    filename = sys.argv[1]
    import_fp(filename)
