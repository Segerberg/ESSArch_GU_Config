import csv
import sys
import json
import sys
import uuid
from os import listdir
from os.path import isfile, join

import django
django.setup()
from countries_plus.models import Country
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models, transaction
from django.utils import timezone
from elasticsearch import helpers as es_helpers
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import get_connection as get_es_connection
from languages_plus.models import Language

from ESSArch_Core.agents.documents import AgentDocument
from ESSArch_Core.agents.models import (
    Agent,
    AgentIdentifier,
    AgentIdentifierType,
    AgentName,
    AgentNameType,
    AgentTagLink,
    AgentTagLinkRelationType,
    AgentType,
    MainAgentType,
    RefCode,
)
from ESSArch_Core.auth.models import (
    Group,
    GroupGenericObjects,
    GroupMemberRole,
    GroupType,
    Member,
)
from ESSArch_Core.tags.documents import (
    Archive,
    Component,
    File,
    StructureUnitDocument,
)
from ESSArch_Core.tags.models import (
    Structure,
    StructureType,
    StructureUnit,
    StructureUnitType,
    Tag,
    TagStructure,
    TagVersion,
    TagVersionType,
)
from ESSArch_Core.WorkflowEngine.models import ProcessTask
#from install_default_ark import installDefaultConfiguration



User = get_user_model()
org_group_type, _ = GroupType.objects.get_or_create(label='organization')


def create_default_structure(structure_name):
    structure_type, _ = StructureType.objects.get_or_create(
        name=structure_name)
    Structure.objects.get_or_create(name='default', type=structure_type, is_template=True,
                                         published=True)

def create_new_group(groupname, id):
    group, _ = Group.objects.get_or_create(
        name=groupname, group_type=org_group_type)
    return group


def cleanup(task):
    conn = get_es_connection()
    Search(using=conn, index='_all').query(
        'term', task_id=str(task.pk)).delete()
    Agent.objects.filter(task=task).delete()
    Tag.objects.filter(task=task).delete()


def save_to_elasticsearch(task):
    conn = get_es_connection()
    print('Saving to elasticsearch')

    agents = AgentDocument.from_queryset(
        Agent.objects.filter(task=task).all(), to_dict=True)
    for ok, result in es_helpers.streaming_bulk(conn, agents):
        pass

    archives = Archive.from_queryset(TagVersion.objects.filter(type__archive_type=True, tag__task=task).all(),
                                     to_dict=True)
    for ok, result in es_helpers.streaming_bulk(conn, archives):
        pass

    units = StructureUnitDocument.from_queryset(StructureUnit.objects.filter(
        task=task, structure__is_template=False).all(), to_dict=True)
    for ok, result in es_helpers.streaming_bulk(conn, units):
        pass


def main(filename):

    #import_files = [f for f in listdir(path) if isfile(join(path, f))]
    cache.clear()
    task, _ = ProcessTask.objects.get_or_create(name="org_import")
    task.reset()
    cleanup(task)
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        reader.__next__()

        for auth_name, auth_id, altname, group in reader:
            auth_name = '{}{}'.format(auth_name[:1].upper(), auth_name[1:].lower())

            new_group = create_new_group(
                group, str(uuid.uuid4()))

            main_agent_type, _ = MainAgentType.objects.get_or_create(
                name='statlig')

            agent_typ, _ = AgentType.objects.get_or_create(
                sub_type='statlig', main_type=main_agent_type)

            agent_identifier_type, _ = AgentIdentifierType.objects.get_or_create(
                name='Organisationsnummer')


            agent_name_type, _ = AgentNameType.objects.get_or_create(
                name='auktoriserad', authority=True)
            agent_par_name_type, _ = AgentNameType.objects.get_or_create(
                name='alternativ', authority=False)
            language = Language.objects.get(iso_639_1='sv')

            ARKIVBILDARE, _ = AgentTagLinkRelationType.objects.get_or_create(
                name='arkivbildare')

            ref_code, _ = RefCode.objects.get_or_create(
                country=Country.objects.get(iso='SE'), repository_code='GU001',)

            new_agent, _ = Agent.objects.get_or_create(
                identifiers__identifier='GU',
                identifiers__type=agent_identifier_type,

                defaults={
                    'type': agent_typ,
                    'level_of_detail': Agent.MINIMAL,
                    'record_status': Agent.DRAFT,
                    'script': Agent.LATIN,
                    'language': language,
                    'ref_code': ref_code,
                    'create_date': timezone.now(),
                    'start_date': None,
                    'end_date': None

                }
            )

            AgentIdentifier.objects.get_or_create(
                type=agent_identifier_type,
                identifier=auth_id,
                agent=new_agent
            )

            AgentName.objects.get_or_create(
                agent=new_agent,
                main=auth_name,
                type=agent_name_type,
            )

            if len(altname) > 0:

                AgentName.objects.get_or_create(
                    agent=new_agent,
                    main=altname,
                    type=agent_par_name_type,
                )

            ctype = ContentType.objects.get_for_model(Agent)
            GroupGenericObjects.objects.update_or_create(content_type=ctype, object_id=new_agent.pk,
                                                         defaults={'group': new_group})
            ###SKAPA ARKIV ###

            arkivtyp, _ = TagVersionType.objects.get_or_create(
                name='Arkiv', archive_type=True)

            #structure_template = Structure.objects.get(name=val[0],  is_template=True)
            structure_template = Structure.objects.get(
                name='Klassificeringsstruktur Göteborgs universitet', is_template=True)
            archive_tag = Tag.objects.create()
            archive_tag_version = TagVersion.objects.create(tag=archive_tag, elastic_index='archive', name='{}s Arkiv'.format(auth_name), type=arkivtyp,
                                                            reference_code='arkiv-{}'.format(auth_id))
            archive_tag.current_version = archive_tag_version
            archive_tag.save()
            structure_instance, archive_tag_structure = structure_template.create_template_instance(
                archive_tag)
            structure_instance.units.update()
            doc = Archive.from_obj(archive_tag_version)
            doc.save()

            link = AgentTagLink.objects.create(
                type=ARKIVBILDARE,
                agent=new_agent,
                tag=archive_tag_version,
            )
            ctype = ContentType.objects.get_for_model(TagVersion)
            GroupGenericObjects.objects.update_or_create(content_type=ctype, object_id=archive_tag_version.pk,
                                                         defaults={'group': new_group})

            structure_instance.units.update()


if __name__ == '__main__':
    #installDefaultConfiguration()
    create_default_structure('Klassificeringsstruktur Göteborgs universitet')
    filename = sys.argv[1]
    task = main(filename)
    save_to_elasticsearch(task)
    # create_users()







