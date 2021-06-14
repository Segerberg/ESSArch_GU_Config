# -*- coding: UTF-8 -*-

"""
    ESSArch is an open source archiving and digital preservation system

    ESSArch
    Copyright (C) 2005-2019 ES Solutions AB

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

    Contact information:
    Web - http://www.essolutions.se
    Email - essarch@essolutions.se
"""

import django

django.setup()

from countries_plus.models import Country
from ESSArch_Core.tags.models import (
    DeliveryType,
    LocationLevelType,
    LocationFunctionType,
    MetricType,
    NodeIdentifierType,
    NodeNoteType,
    NodeRelationType,
    StructureType,
    RuleConventionType,
    StructureUnitType,
    MetricType,
    TagVersionType,

)
from ESSArch_Core.agents.models import (
    AgentIdentifierType,
    AgentNameType,
    AgentNoteType,
    AgentPlaceType,
    AgentRelationType,
    AgentTagLinkRelationType,
    AgentType,
    AuthorityType,
    SourcesOfAuthority,
    RefCode,
    MainAgentType,
)

from ESSArch_Core.ip.models import (
    ConsignMethod,
    OrderType,
)

def installDefaultConfiguration():
    print("Installing RefCodes...")
    installDefaultRefCodes()
    print("Installing AgentIdentifierTypes...")
    installDefaultAgentIdentifierTypes()
    print("Installing AgentNameTypes...")
    installDefaultAgentNameTypes()
    print("Installing AgentNoteTypes...")
    installDefaultAgentNoteTypes()
    print("Installing AgentPlaceTypes...")
    installDefaultAgentPlaceTypes()
    print("Installing AgentRelationTypes...")
    installDefaultAgentRelationTypes()
    print("Installing AgentTagLinkRelationTypes...")
    installDefaultAgentTagLinkRelationTypes()
    print("Installing MainAgentTypes...")
    installDefaultMainAgentTypes()
    print("Installing AgentTypes...")
    installDefaultAgentTypes()
    print("Installing AuthorityTypes...")
    installDefaultAuthorityTypes()
    print("Installing DeliveryTypes...")
    installDefaultDeliveryTypes()
    print("Installing LocationLevelTypes...")
    installDefaulLocationLevelTypes()
    print("Installing LocationFunctionTypes...")
    installDefaulLocationFunctionTypes()
    print("Installing MetricTypes...")
    installDefaulMetricTypes()
    print("Installing NodeIdentifierTypes...")
    installDefaultNodeIdentifierTypes()
    print("Installing NodeNoteTypes...")
    installDefaultNodeNoteTypes()
    print("Installing NodeRelationTypes...")
    installDefaultNodeRelationTypes()
    print("Installing TagVersionTypes...")
    installDefaultTagVersionTypes()
    print("Installing StructureTypes...")
    installDefaultStructureTypes()
    print("Installing StructureUnitTypes...")
    installDefaultStructureUnitTypes()
    print("Installing CosignTypes...")
    installDefaultConsignTypes()
    print("Installing OrderTypes...")
    installDefaultOrderTypes()


    return 0

def installDefaultRefCodes():
    vals = [
        '321',
    ]
    country = Country.objects.get(name="Sweden")

    for val in vals:
        print('-> %s' % (val))
        RefCode.objects.update_or_create(repository_code=val, country=country)

    return 0

def installDefaultConsignTypes():
    vals = [
        'epost',
        'folkbokföringsadress',
        'hämtas'
    ]

    for val in vals:
        print('-> %s' % (val))
        ConsignMethod.objects.update_or_create(name=val,)

    return 0

def installDefaultOrderTypes():
    vals = [
        'beställning',
    ]

    for val in vals:
        print('-> %s' % (val))
        OrderType.objects.update_or_create(name=val,)

    return 0

def installDefaultAgentIdentifierTypes():
    vals = [
        'orgnr',
    ]

    for val in vals:
        print('-> %s' % (val))
        AgentIdentifierType.objects.update_or_create(name=val,)

    return 0


def installDefaultAgentNameTypes():
    vals = [
        'auktoriserad',
        'förkortning',
        'översättning',
        'alternativ',
        'övrig alternativ namnform',
    ]

    for idx, val in enumerate(vals):
        print('-> %s' % (val))
        authority = idx == 0
        AgentNameType.objects.update_or_create(name=val, authority=authority)

    return 0


def installDefaultAgentNoteTypes():
    vals = [
        'historik',
        'administrativ anmärkning',
        'allmän anmärkning',
    ]

    for idx, val in enumerate(vals):
        print('-> %s' % (val))
        history = idx == 0
        AgentNoteType.objects.update_or_create(name=val, history=history)

    return 0


def installDefaultAgentPlaceTypes():
    vals = [
        'verksamhetsort',
        'lokaliseringssort',
        'födelseort',
        'dödsort',
    ]

    for val in vals:
        print('-> %s' % (val))
        AgentPlaceType.objects.update_or_create(name=val,)

    return 0


def installDefaultAgentRelationTypes():
    dct = {
        'föregångare till': {'mirrored_type': 'efterföljare till'},
        'efterföljare till': {'mirrored_type': 'föregångare till'},
        'underordnad': {'mirrored_type': 'överordnad'},
        'överordnad': {'mirrored_type': 'underordnad'},
        'associerad': {'mirrored_type': 'associerad'},
    }

    for key, val in dct.items():
        AgentRelationType.objects.update_or_create(
            name=key,
        )
    for key, val in dct.items():
        print('-> %s: %s' % (key, val['mirrored_type']))

        mirrored = AgentRelationType.objects.get(name=val['mirrored_type'])
        AgentRelationType.objects.update_or_create(
            name=key,
            defaults={'mirrored_type': mirrored}
        )

    return 0


def installDefaultAgentTagLinkRelationTypes():
    dict = {
        'arkivbildare': {'creator': True},
        'arkivansvarig': {'creator': False},
    }

    for key, val in dict.items():
        print('-> %s: %s' % (key, val['creator']))
        AgentTagLinkRelationType.objects.update_or_create(
            name=key,
            defaults={'creator': val['creator']}
        )

    return 0


def installDefaultMainAgentTypes():
    vals = [
        'statlig',
        'enskild',
    ]

    for val in vals:
        print('-> %s' % (val))
        MainAgentType.objects.update_or_create(name=val,)

    return 0


def installDefaultAgentTypes():
    dct = {
        'förening': {'main_type': 'enskild', 'cpf': 'corporatebody'},
        'person': {'main_type': 'enskild', 'cpf': 'person'},
        'statlig': {'main_type': 'statlig', 'cpf': 'corporatebody'},

    }

    for key, val in dct.items():
        print('-> %s: %s' % (key, val['main_type']))

        main_type = MainAgentType.objects.get(name=val['main_type'])
        AgentType.objects.update_or_create(
            sub_type=key,
            defaults={'main_type': main_type, 'cpf': val['cpf']}
        )

    return 0


def installDefaultAuthorityTypes():
    vals = [
        'konstituerande protokoll',
        'instruktion',
    ]

    for val in vals:
        print('-> %s' % (val))
        AuthorityType.objects.update_or_create(name=val,)

    return 0


def installDefaultDeliveryTypes():
    vals = [
        'deposition',
        'gåva',
        'leverans',
    ]

    for val in vals:
        print('-> %s' % (val))
        DeliveryType.objects.update_or_create(name=val,)

    return 0


def installDefaulLocationLevelTypes():
    vals = [
        'byggnad',
        'våning',
        'rum',
        'hylla',
        'hyllsektion',
        'ritningsskåp',
        'dokumentskåp'
    ]

    for val in vals:
        print('-> %s' % (val))
        LocationLevelType.objects.update_or_create(
            name=val,
        )

    return 0


def installDefaulLocationFunctionTypes():
    vals = ['tills vidare', 'tillfällig']

    for val in vals:
        print('-> %s' % (val))
        LocationFunctionType.objects.update_or_create(name=val,)

    return 0


def installDefaulMetricTypes():
    vals = ['meter', 'centimeter', 'millimeter']

    for val in vals:
        print('-> %s' % (val))
        MetricType.objects.update_or_create(name=val,)

    return 0


def installDefaultNodeIdentifierTypes():
    vals = ['Eget id']
    for val in vals:
        print('-> %s' % (val))
        NodeIdentifierType.objects.update_or_create(name=val,)

    return 0


def installDefaultNodeNoteTypes():
    vals = [
        'historik',
        'administrativ anmärkning',
        'allmän anmärkning',
    ]

    for val in vals:
        print('-> %s' % (val))
        NodeNoteType.objects.update_or_create(name=val,)

    return 0


def installDefaultNodeRelationTypes():
    dct = {
        'ingår i': {'mirrored_type': 'här i även'},
        'här i även': {'mirrored_type': 'ingår i'},
        'bildas i': {'mirrored_type': 'avsätts i'},
        'avsätts i': {'mirrored_type': 'bildas i'},

    }

    for key, val in dct.items():
        NodeRelationType.objects.update_or_create(
            name=key,
        )
    for key, val in dct.items():
        print('-> %s: %s' % (key, val['mirrored_type']))

        mirrored = NodeRelationType.objects.get(name=val['mirrored_type'])
        NodeRelationType.objects.update_or_create(
            name=key,
            defaults={'mirrored_type': mirrored}
        )

    return 0


def installDefaultTagVersionTypes():
    dct = {
        'Arkiv': {'archive_type': True},
        'Samling': {'archive_type': True},
        'Volym': {'archive_type': False},
        'AIP': {'archive_type': False, 'information_package_type': True},
    }

    for key, val in dct.items():
        print('-> %s: archive_type ==  %s' % (key, val['archive_type']))
        TagVersionType.objects.update_or_create(
            name=key,
            defaults={'archive_type': val['archive_type'], 'information_package_type': val.get('information_package_type', False)}
        )

    return 0


def installDefaultStructureTypes():
    dct = {
        'klassificeringsstruktur': {'instance_name': 'klassificeringsstruktur', 'editable_instances': True, 'editable_instance_relations': True, 'movable_instance_units': True},
        'förteckningsplan': {'instance_name': 'förteckning', 'editable_instances': True, 'editable_instance_relations': True, 'movable_instance_units': True},
        'förteckningsplan vba': {'instance_name': 'förteckning', 'editable_instances': True, 'editable_instance_relations': True, 'movable_instance_units': True},
    }

    for key, val in dct.items():
        print('-> %s: %s' % (key, val))

        StructureType.objects.update_or_create(
            name=key,
            defaults={
                'instance_name': val['instance_name'],
                'editable_instances': val['editable_instances'],
                'editable_instance_relations': val['editable_instance_relations'],
                'movable_instance_units': val['movable_instance_units']}
        )

    return 0


def installDefaultStructureUnitTypes():
    dct = {
        'verksamhetsområde': {'structure_type': 'klassificeringsstruktur'},
        'processgrupp': {'structure_type': 'klassificeringsstruktur'},
        'process': {'structure_type': 'klassificeringsstruktur'},
        'serie': {'structure_type': 'förteckningsplan'},
        'handlingsslag': {'structure_type': 'förteckningsplan vba'},
        'handlingstyp': {'structure_type': 'förteckningsplan vba'},
    }

    for key, val in dct.items():
        print('-> %s: %s' % (key, val['structure_type']))

        structure_type = StructureType.objects.get(name=val['structure_type'])
        StructureUnitType.objects.update_or_create(
            name=key,
            defaults={'structure_type': structure_type}
        )

    return 0


print('done')


if __name__ == '__main__':
    installDefaultConfiguration()
