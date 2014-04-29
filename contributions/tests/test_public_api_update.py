import json

from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory, force_authenticate

from nose.tools import raises

from projects.tests.model_factories import UserF, UserGroupF, ProjectF
from dataviews.tests.model_factories import ViewFactory, ViewGroupFactory
from observationtypes.tests.model_factories import (
    ObservationTypeFactory, TextFieldFactory, NumericFieldFactory
)
from contributions.models import Observation

from .model_factories import LocationFactory
from ..views import SingleObservation


class UpdateObservation(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.view_member = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        self.observationtype = ObservationTypeFactory(**{
            'status': 'active',
            'project': self.project
        })

        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.project
            })
        })

        TextFieldFactory.create(**{
            'key': 'key_1',
            'observationtype': self.observationtype
        })
        NumericFieldFactory.create(**{
            'key': 'key_2',
            'observationtype': self.observationtype
        })

        location = LocationFactory()

        self.observation = Observation.create(
            attributes={
                "key_1": "value 1",
                "key_2": 12,
            },
            observationtype=self.observationtype,
            project=self.project,
            location=location,
            creator=self.admin
        )

        self.update_data = {
            "properties": {
                "version": 1,
                "key_2": 15,
            }
        }

    def _put(self, data, user):
        url = reverse(
            'api:project_single_observation',
            kwargs={
                'project_id': self.project.id,
                'observation_id': self.observation.id
            }
        )
        request = self.factory.put(url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=user)
        view = SingleObservation.as_view()
        return view(
            request, project_id=self.project.id,
            observation_id=self.observation.id).render()

    def _delete(self, user):
        url = reverse(
            'api:project_single_observation',
            kwargs={
                'project_id': self.project.id,
                'observation_id': self.observation.id
            }
        )
        request = self.factory.delete(url, content_type='application/json')
        force_authenticate(request, user=user)
        view = SingleObservation.as_view()
        return view(
            request, project_id=self.project.id,
            observation_id=self.observation.id).render()

    def test_update_without_version(self):
        data = {"properties": {"key_2": 15}}

        response = self._put(
            data,
            self.admin
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_update_with_wrong_version(self):
        data = {"properties": {"version": 3000, "key_2": 15}}

        response = self._put(
            data,
            self.admin
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_update_conflict(self):
        response = self._put(
            self.update_data,
            self.admin
        )
        self.assertEqual(response.status_code, 200)

        data = {"properties": {"version": 1, "key_2": 2}}
        response = self._put(
            data,
            self.contributor
        )
        self.assertEqual(response.status_code, 200)

    def test_updated_deleted_observation(self):
        self.observation.status = 'deleted'
        self.observation.save()

        response = self._put(
            self.update_data,
            self.admin
        )
        self.assertEqual(response.status_code, 404)

    def test_update_to_public_with_admin(self):
        self.project.isprivate = False
        self.project.save()

        response = self._put(
            self.update_data,
            self.admin
        )
        self.assertEqual(response.status_code, 200)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(
            observation.attributes.get('key_2'), '15')

    @raises(Observation.DoesNotExist)
    def test_delete_public_with_admin(self):
        self.project.isprivate = False
        self.project.save()

        response = self._delete(
            self.admin
        )
        self.assertEqual(response.status_code, 204)
        Observation.objects.get(pk=self.observation.id)

    def test_update_to_public_with_contributor(self):
        self.project.isprivate = False
        self.project.save()

        response = self._put(
            self.update_data,
            self.contributor
        )
        self.assertEqual(response.status_code, 200)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(
            observation.attributes.get('key_2'), '15')

    @raises(Observation.DoesNotExist)
    def test_delete_public_with_contributor(self):
        self.project.isprivate = False
        self.project.save()

        response = self._delete(
            self.contributor
        )
        self.assertEqual(response.status_code, 204)
        Observation.objects.get(pk=self.observation.id)

    def test_update_to_public_with_view_member(self):
        self.project.isprivate = False
        self.project.save()

        response = self._put(
            self.update_data,
            self.view_member
        )
        self.assertEqual(response.status_code, 403)

        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_delete_public_with_view_member(self):
        self.project.isprivate = False
        self.project.save()

        response = self._delete(
            self.view_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'deleted'
        )

    def test_update_to_public_with_non_member(self):
        self.project.isprivate = False
        self.project.save()

        response = self._put(
            self.update_data,
            self.non_member
        )
        self.assertEqual(response.status_code, 403)

        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_delete_public_with_non_member(self):
        self.project.isprivate = False
        self.project.save()

        response = self._delete(
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'deleted'
        )

    def test_update_to_public_everyone_with_admin(self):
        self.project.isprivate = False
        self.project.everyonecontributes = True
        self.project.save()

        response = self._put(
            self.update_data,
            self.admin
        )
        self.assertEqual(response.status_code, 200)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(
            observation.attributes.get('key_2'), '15')

    @raises(Observation.DoesNotExist)
    def test_delete_public_everyone_with_admin(self):
        self.project.isprivate = False
        self.project.everyonecontributes = True
        self.project.save()

        response = self._delete(
            self.admin
        )
        self.assertEqual(response.status_code, 204)
        Observation.objects.get(pk=self.observation.id)

    def test_update_to_public_everyone_with_contributor(self):
        self.project.isprivate = False
        self.project.everyonecontributes = True
        self.project.save()

        response = self._put(
            self.update_data,
            self.contributor
        )
        self.assertEqual(response.status_code, 200)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(
            observation.attributes.get('key_2'), '15')

    @raises(Observation.DoesNotExist)
    def test_delete_public_everyone_with_contributor(self):
        self.project.isprivate = False
        self.project.everyonecontributes = True
        self.project.save()

        response = self._delete(
            self.contributor
        )
        self.assertEqual(response.status_code, 204)
        Observation.objects.get(pk=self.observation.id)

    def test_update_to_public_everyone_with_view_member(self):
        self.project.isprivate = False
        self.project.everyonecontributes = True
        self.project.save()

        response = self._put(
            self.update_data,
            self.view_member
        )
        self.assertEqual(response.status_code, 200)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(
            observation.attributes.get('key_2'), '15')

    @raises(Observation.DoesNotExist)
    def test_delete_public_everyone_with_view_member(self):
        self.project.isprivate = False
        self.project.everyonecontributes = True
        self.project.save()

        response = self._delete(
            self.view_member
        )
        self.assertEqual(response.status_code, 204)
        Observation.objects.get(pk=self.observation.id)

    def test_update_to_public_everyone_with_non_member(self):
        self.project.isprivate = False
        self.project.everyonecontributes = True
        self.project.save()

        response = self._put(
            self.update_data,
            self.non_member
        )
        self.assertEqual(response.status_code, 200)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(
            observation.attributes.get('key_2'), '15')

    @raises(Observation.DoesNotExist)
    def test_delete_public_everyone_with_non_member(self):
        self.project.isprivate = False
        self.project.everyonecontributes = True
        self.project.save()

        response = self._delete(
            self.non_member
        )
        self.assertEqual(response.status_code, 204)
        Observation.objects.get(pk=self.observation.id)

    def test_update_to_private_with_admin(self):
        response = self._put(
            self.update_data,
            self.admin
        )
        self.assertEqual(response.status_code, 200)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(
            observation.attributes.get('key_2'), '15')

    @raises(Observation.DoesNotExist)
    def test_delete_private_with_admin(self):
        response = self._delete(
            self.admin
        )
        self.assertEqual(response.status_code, 204)
        Observation.objects.get(pk=self.observation.id)

    def test_update_to_private_with_contributor(self):
        response = self._put(
            self.update_data,
            self.contributor
        )
        self.assertEqual(response.status_code, 200)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(
            observation.attributes.get('key_2'), '15')

    @raises(Observation.DoesNotExist)
    def test_delete_private_with_contributor(self):
        response = self._delete(
            self.contributor
        )
        self.assertEqual(response.status_code, 204)
        Observation.objects.get(pk=self.observation.id)

    def test_update_to_private_with_view_member(self):
        response = self._put(
            self.update_data,
            self.view_member
        )
        self.assertEqual(response.status_code, 403)

        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_delete_private_with_view_member(self):
        response = self._delete(
            self.view_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'deleted'
        )

    def test_update_to_private_with_non_member(self):
        response = self._put(
            self.update_data,
            self.non_member
        )
        self.assertEqual(response.status_code, 403)

        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_delete_private_with_non_member(self):
        response = self._delete(
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'deleted'
        )

    def test_update_to_private_everyone_with_admin(self):
        self.project.everyonecontributes = True
        self.project.save()

        response = self._put(
            self.update_data,
            self.admin
        )
        self.assertEqual(response.status_code, 200)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(
            observation.attributes.get('key_2'), '15')

    @raises(Observation.DoesNotExist)
    def test_delete_private_everyone_with_admin(self):
        self.project.everyonecontributes = True
        self.project.save()

        response = self._delete(
            self.admin
        )
        self.assertEqual(response.status_code, 204)
        Observation.objects.get(pk=self.observation.id)

    def test_update_to_private_everyone_with_contributor(self):
        self.project.everyonecontributes = True
        self.project.save()

        response = self._put(
            self.update_data,
            self.contributor
        )
        self.assertEqual(response.status_code, 200)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(
            observation.attributes.get('key_2'), '15')

    @raises(Observation.DoesNotExist)
    def test_delete_private_everyone_with_contributor(self):
        self.project.everyonecontributes = True
        self.project.save()

        response = self._delete(
            self.contributor
        )
        self.assertEqual(response.status_code, 204)
        Observation.objects.get(pk=self.observation.id)

    def test_update_to_private_everyone_with_view_member(self):
        self.project.everyonecontributes = True
        self.project.save()

        response = self._put(
            self.update_data,
            self.view_member
        )
        self.assertEqual(response.status_code, 200)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(
            observation.attributes.get('key_2'), '15')

    @raises(Observation.DoesNotExist)
    def test_delete_private_everyone_with_view_member(self):
        self.project.everyonecontributes = True
        self.project.save()

        response = self._delete(
            self.view_member
        )
        self.assertEqual(response.status_code, 204)
        Observation.objects.get(pk=self.observation.id)

    def test_update_to_private_everyone_with_non_member(self):
        self.project.everyonecontributes = True
        self.project.save()

        response = self._put(
            self.update_data,
            self.non_member
        )
        self.assertEqual(response.status_code, 403)

        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_delete_private_everyone_with_non_member(self):
        self.project.everyonecontributes = True
        self.project.save()

        response = self._delete(
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'deleted'
        )

    def test_update_to_inactive_with_admin(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._put(
            self.update_data,
            self.admin
        )
        self.assertEqual(response.status_code, 403)

        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_delete_inactive_with_admin(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._delete(
            self.admin
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'deleted'
        )

    def test_update_to_inactive_with_contributor(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._put(
            self.update_data,
            self.contributor
        )
        self.assertEqual(response.status_code, 403)

        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_delete_inactive_with_contributor(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._delete(
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'deleted'
        )

    def test_update_to_inactive_with_view_member(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._put(
            self.update_data,
            self.view_member
        )
        self.assertEqual(response.status_code, 403)

        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_delete_inactive_with_view_member(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._delete(
            self.view_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'deleted'
        )

    def test_update_to_inactive_with_non_member(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._put(
            self.update_data,
            self.non_member
        )
        self.assertEqual(response.status_code, 403)

        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_delete_inactive_with_non_member(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._delete(
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'deleted'
        )

    def test_update_to_deleted_with_admin(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._put(
            self.update_data,
            self.admin
        )
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_delete_deleted_with_admin(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._delete(
            self.admin
        )
        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'deleted'
        )

    def test_update_to_deleted_with_contributor(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._put(
            self.update_data,
            self.contributor
        )
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_delete_deleted_with_contributor(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._delete(
            self.contributor
        )
        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'deleted'
        )

    def test_update_to_deleted_with_view_member(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._put(
            self.update_data,
            self.view_member
        )
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_delete_deleted_with_view_member(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._delete(
            self.view_member
        )
        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'deleted'
        )

    def test_update_to_deleted_with_non_member(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._put(
            self.update_data,
            self.non_member
        )
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.observation.attributes.get('key_2'), '12')

    def test_delete_deleted_with_non_member(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._delete(
            self.non_member
        )
        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'deleted'
        )
