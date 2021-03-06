import json

from core.exceptions import MalformedRequestData
from django.core.exceptions import ValidationError
from django.test import TestCase
from nose.tools import raises

from projects.tests.model_factories import UserF, ProjectF
from categories.tests.model_factories import (
    CategoryFactory, TextFieldFactory, NumericFieldFactory
)

from ..serializers import ContributionSerializer
from ..models import Observation
from .model_factories import LocationFactory, ObservationFactory


class RestoreLocationTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()

        self.project = ProjectF(
            add_admins=[self.admin]
        )
        self.category = CategoryFactory(**{
            'status': 'active',
            'project': self.project
        })

        TextFieldFactory.create(**{
            'key': 'key_1',
            'category': self.category
        })
        NumericFieldFactory.create(**{
            'key': 'key_2',
            'category': self.category
        })

        self.data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.134046077728271,
                    51.52439200896907
                ]
            },
            "properties": {
                "attributes": {
                    "key_1": "value 1",
                    "key_2": 12
                },
                "category": self.category.id,
                "location": {
                    "name": "UCL",
                    "description": "UCL's main quad",
                    "private": True
                },
            }
        }

    def test_restore_new_location(self):
        user = UserF.create()
        data = {
            "name": "UCL",
            "description": "UCL's main quad",
            "private": True
        }
        geometry = {
            "type": "Point",
            "coordinates": [
                -0.134046077728271,
                51.52439200896907
            ]
        }
        serializer = ContributionSerializer(
            data=self.data,
            context={'user': user, 'project': self.project}
        )
        location = serializer.restore_location(data=data, geometry=geometry)

        self.assertEqual(location.creator, user)
        self.assertEqual(location.name, 'UCL')
        self.assertEqual(location.description, "UCL's main quad")
        self.assertTrue(location.private)
        self.assertEqual(location.private_for_project, None)
        self.assertEqual(json.loads(location.geometry.geojson), geometry)

    def test_restore_unspecified_location(self):
        geometry = {
            "type": "Point",
            "coordinates": [
                -0.134046077728271,
                51.52439200896907
            ]
        }
        serializer = ContributionSerializer(
            data=self.data,
            context={'user': self.admin, 'project': self.project}
        )
        location = serializer.restore_location(geometry=geometry)

        self.assertEqual(location.creator, self.admin)
        self.assertEqual(location.name, None)
        self.assertEqual(location.description, None)
        self.assertFalse(location.private)
        self.assertEqual(location.private_for_project, None)
        self.assertEqual(json.loads(location.geometry.geojson), geometry)

    def test_restore_existing_location(self):
        location = LocationFactory()
        serializer = ContributionSerializer(
            data=self.data,
            context={'user': self.admin, 'project': self.project}
        )

        data = {
            "id": location.id,
            "name": location.name,
            "description": location.description,
            "private": location.private
        }
        geometry = json.loads(location.geometry.geojson)

        result = serializer.restore_location(data=data, geometry=geometry)
        self.assertEqual(location, result)


class ContributionSerializerIntegrationTests(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.view_member = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member]
        )
        self.category = CategoryFactory(**{
            'status': 'active',
            'project': self.project
        })

        TextFieldFactory.create(**{
            'key': 'key_1',
            'category': self.category
        })
        NumericFieldFactory.create(**{
            'key': 'key_2',
            'category': self.category
        })

    def test_create_observation(self):
        data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.134046077728271,
                    51.52439200896907
                ]
            },
            "properties": {
                "attributes": {
                    "key_1": "value 1",
                    "key_2": 12
                },
                "category": self.category.id,
                "location": {
                    "name": "UCL",
                    "description": "UCL's main quad",
                    "private": True
                },
            }
        }

        serializer = ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )
        result = serializer.data

        self.assertEqual(result.get('type'), 'Feature')
        self.assertEqual(result.get('geometry'), data.get('geometry'))
        self.assertEqual(
            result.get('properties').get('attributes').get('key_1'),
            'value 1'
        )
        self.assertEqual(
            result.get('properties').get('attributes').get('key_2'),
            12
        )
        self.assertEqual(
            result.get('category').get('id'),
            self.category.id)
        self.assertEqual(
            result.get('properties').get('location').get('name'), 'UCL')
        self.assertEqual(
            result.get('properties').get('location').get('description'),
            "UCL's main quad")

    def test_create_without_speficfied_location(self):
        data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.134046077728271,
                    51.52439200896907
                ]
            },
            "properties": {
                "attributes": {
                    "key_1": "value 1",
                    "key_2": 12
                },
                "category": self.category.id
            }
        }

        serializer = ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )
        result = serializer.data

        self.assertEqual(result.get('type'), 'Feature')
        self.assertEqual(result.get('geometry'), data.get('geometry'))
        self.assertEqual(
            result.get('properties').get('attributes').get('key_1'),
            'value 1'
        )
        self.assertEqual(
            result.get('properties').get('attributes').get('key_2'),
            12
        )
        self.assertEqual(
            result.get('category').get('id'),
            self.category.id)
        self.assertEqual(
            result.get('properties').get('location').get('name'), None)
        self.assertEqual(
            result.get('properties').get('location').get('description'),
            None)

    def test_create_with_existing_location(self):
        location = LocationFactory.create()

        data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    location.geometry.coords[0],
                    location.geometry.coords[1]
                ]
            },
            "properties": {
                "attributes": {
                    "key_1": "value 1",
                    "key_2": 12
                },
                "category": self.category.id,
                "location": {"id": location.id}
            }
        }

        serializer = ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )
        result = serializer.data

        self.assertEqual(result.get('type'), 'Feature')
        self.assertEqual(result.get('geometry'), data.get('geometry'))
        self.assertEqual(
            result.get('properties').get('attributes').get('key_1'),
            'value 1'
        )
        self.assertEqual(
            result.get('properties').get('attributes').get('key_2'),
            12
        )
        self.assertEqual(
            result.get('category').get('id'),
            self.category.id)
        self.assertEqual(
            result.get('properties').get('location').get('name'),
            location.name)
        self.assertEqual(
            result.get('properties').get('location').get('description'),
            location.description)

    @raises(MalformedRequestData)
    def test_create_with_wrong_location(self):
        project = ProjectF()
        location = LocationFactory(**{
            'private': True,
            'private_for_project': project
        })

        data = {
            "type": "Feature",
            "geometry": location.geometry.geojson,
            "properties": {
                "location": {"id": location.id},
                "category": self.category.id,
                "attributes": {
                    "key_1": "value 1",
                    "key_2": 12
                }
            }
        }
        ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )

    @raises(MalformedRequestData)
    def test_create_with_private_location(self):
        location = LocationFactory(**{'private': True})
        data = {
            "type": "Feature",
            "geometry": location.geometry.geojson,
            "properties": {
                "location": {"id": location.id},
                "category": self.category.id,
                "attributes": {
                    "key_1": "value 1",
                    "key_2": 12
                }
            }
        }
        ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )

    @raises(ValidationError)
    def test_create_with_invalid_data(self):
        data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.134046077728271,
                    51.52439200896907
                ]
            },
            "properties": {
                "attributes": {
                    "key_1": "value 1",
                    "key_2": "blah"
                },
                "category": self.category.id,
                "location": {
                    "name": "UCL",
                    "description": "UCL's main quad",
                    "private": True
                },
            }
        }
        ContributionSerializer(
            data=data,
            context={'user': self.contributor, 'project': self.project}
        )

    def test_serialize_instance(self):
        observation = ObservationFactory.create(
            **{'attributes': {'key': 'value'}}
        )
        TextFieldFactory.create(**{
            'key': 'key',
            'category': observation.category})
        serializer = ContributionSerializer(
            observation,
            context={'user': self.contributor, 'project': self.project}
        )
        result = serializer.data

        self.assertEqual(result.get('type'), 'Feature')
        self.assertEqual(
            result.get('geometry'),
            json.loads(observation.location.geometry.geojson))
        self.assertEqual(
            result.get('properties').get('attributes').get('key'),
            'value'
        )
        self.assertEqual(
            result.get('category').get('id'),
            observation.category.id)
        self.assertEqual(
            result.get('properties').get('location').get('name'),
            observation.location.name)
        self.assertEqual(
            result.get('properties').get('location').get('description'),
            observation.location.description)

    def test_serialize_bulk(self):
        number = 20

        ObservationFactory.create_batch(number)
        observations = Observation.objects.prefetch_related(
            'location', 'category', 'creator', 'updator')

        serializer = ContributionSerializer(
            observations,
            many=True,
            context={'user': self.contributor, 'project': self.project}
        )
        result = serializer.data

        self.assertEqual(result.get('type'), 'FeatureCollection')
        self.assertEqual(len(result.get('features')), number)

        for f in result.get('features'):
            self.assertIsNone(f.get('search_matches'))

    def test_serialize_bulk_search(self):
        number = 20

        o_type = CategoryFactory.create()
        TextFieldFactory.create(**{
            'category': o_type,
            'key': 'field-1',
            'order': 0
        })
        TextFieldFactory.create(**{
            'category': o_type,
            'key': 'field-2',
            'order': 1
        })
        TextFieldFactory.create(**{
            'category': o_type,
            'key': 'field-3',
            'order': 2
        })

        ObservationFactory.create_batch(
            number,
            **{
                'attributes': {
                    'field-1': 'blah',
                    'field-2': 'blabla',
                    'field-3': 'sddsdsfdsf'
                },
                'category': o_type
            }
        )
        observations = Observation.objects.prefetch_related(
            'location', 'category', 'creator', 'updator')

        serializer = ContributionSerializer(
            observations,
            many=True,
            context={
                'user': self.contributor,
                'project': self.project,
                'search': 'bla'
            }
        )
        result = serializer.data

        self.assertEqual(result.get('type'), 'FeatureCollection')
        self.assertEqual(len(result.get('features')), number)

        for f in result.get('features'):
            self.assertIsNotNone(f.get('search_matches'))
            self.assertIsNone(
                f.get('search_matches').get('field-3')
            )

    def test_serialize_update(self):
        observation = ObservationFactory.create(
            **{'attributes': {'number': 12}})
        NumericFieldFactory.create(**{
            'key': 'number',
            'category': observation.category})
        serializer = ContributionSerializer(
            observation,
            data={
                'properties': {
                    'attributes': {
                        'number': 15
                    }
                }
            },
            context={'user': self.contributor, 'project': self.project}
        )
        result = serializer.data

        self.assertEqual(
            result.get('properties').get('attributes').get('number'),
            15
        )

    @raises(ValidationError)
    def test_serialize_invalid_update(self):
        observation = ObservationFactory.create(
            **{'attributes': {'number': 12}})
        NumericFieldFactory.create(**{
            'key': 'number',
            'category': observation.category})
        ContributionSerializer(
            observation,
            data={
                'properties': {
                    'attributes': {
                        'number': "blah"
                    }

                }
            },
            context={'user': self.contributor, 'project': self.project}
        )

        o = Observation.objects.get(pk=observation.id)
        self.assertEqual(o.attributes.get('number'), 12)
