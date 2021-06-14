import django
django.setup()


import csv
import sys
import datetime
from django.db import transaction

from ESSArch_Core.tags.models import Structure, StructureType, StructureUnit, StructureUnitType


@transaction.atomic
def import_ks(path):
    with open(path) as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        structure_meta = reader.__next__()
        #structure = Structure.objects.create(name=structure_name)
        structure_type,_ = StructureType.objects.get_or_create(name='klassificeringsstruktur')
        structure = Structure.objects.create(name=structure_meta[0], type=structure_type, is_template=True,
                                             published=True, version=structure_meta[2],
                                             description=structure_meta[3])
        reader.__next__()
        reader.__next__()
        reader.__next__()

        for row in reader:
            if not ''.join(row).strip():
                continue

            try:
                område, process_grp, process1, namn, beskrivning,kommentar = row
                kommentar = ''
            except ValueError:
                område, process_grp, process1, namn, beskrivning,kommentar = row

            for col_name, col_val in [('verksamhetsområde', område), ('processgrupp', process_grp), ('process', process1)]:
                if col_val:
                    #unit_type = col_name
                    unit_type = StructureUnitType.objects.get_or_create(name=col_name, structure_type=structure_type)
                    reference_code = col_val
                    break
            try:
                parent = StructureUnit.objects.get(structure=structure, reference_code=reference_code.rsplit('.', 1)[0])
            except StructureUnit.DoesNotExist:
                parent = None

            StructureUnit.objects.get_or_create(structure=structure, parent=parent, type=unit_type[0], reference_code=reference_code, name=namn, description=beskrivning, comment='')

       # if not StructureUnit.objects.filter(structure=structure, reference_code="9999").exists():
       #     omr_type = StructureUnitType.objects.get_or_create(name='Verksamhetsområde', structure_type=structure_type)
       #     StructureUnit.objects.create(structure=structure, type=omr_type[0], reference_code='9999', name='Migrerad process')


if __name__ == '__main__':
    filename = sys.argv[1]
    import_ks(filename)
