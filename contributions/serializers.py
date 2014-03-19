import json

from django.contrib.gis.geos import GEOSGeometry

from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from core.exceptions import MalformedRequestData
from projects.models import Project
from projects.serializers import ProjectSerializer
from observationtypes.models import ObservationType
from users.serializers import UserSerializer
from observationtypes.serializer import ObservationTypeSerializer

from .models import Location, Observation, ObservationData


class LocationSerializer(serializers.ModelSerializer):
    private_for_project = ProjectSerializer(read_only=True, partial=True)

    class Meta:
        model = Location
        depth = 1
        fields = ('id', 'name', 'description', 'status',
                  'created_at', 'private', 'private_for_project')


class ObservationSerializer(serializers.ModelSerializer):
    observationtype = ObservationTypeSerializer(read_only=True)

    class Meta:
        model = Observation
        depth = 1
        fields = ('id', 'status', 'observationtype')


class ObservationDataSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)

    class Meta:
        model = ObservationData
        depth = 1
        fields = ('created_at', 'creator', 'version')


class ContributionSerializer(object):
    def __init__(self, instance=None, data=None, creator=None):
        properties = data.get('properties')
        try:
            location_data = properties.pop('location')
            observationtype_id = properties.pop('observationtype')
            project_id = properties.pop('project')
        except KeyError:
            pass

        if instance is None:
            #Create a new contribution from the GeoJSON data
            project = Project.objects.as_contributor(creator, project_id)
            try:
                observationtype = ObservationType.objects.get_single(
                    creator,
                    project_id,
                    observationtype_id
                )
            except ObservationType.DoesNotExist:
                raise MalformedRequestData('The observationtype can not be '
                                           'used with the project or does not '
                                           'exist.')

            location = Location.objects.create(
                name=location_data.get('name'),
                description=location_data.get('description'),
                geometry=GEOSGeometry(
                    json.dumps(data.get('geometry'))
                ),
                creator=creator,
                private=location_data.get('private'),
                private_for_project=location_data.get('private_for_project')
            )

            observation = Observation.create(
                data=properties,
                creator=creator,
                location=location,
                project=project,
                observationtype=observationtype
            )
            self.instance = observation
        else:
            self.instance = instance
            self.instance.update(data=properties, creator=creator)

    @property
    def data(self):
        location_serializer = LocationSerializer(self.instance.location)
        observation_serializer = ObservationSerializer(self.instance)
        observation_data_serializer = ObservationDataSerializer(
            self.instance.current_data)
        json_object = {
            'type': 'Feature',
            'geometry': json.loads(self.instance.location.geometry.geojson),
            'properties': {}
        }
        json_object['properties']['location'] = location_serializer.data
        json_object['properties'] = dict(
            observation_serializer.data.items() +
            observation_data_serializer.data.items()
        )
        for field in self.instance.observationtype.fields.all():
            json_object['properties'][field.key] = field.convert_from_string(
                self.instance.current_data.attributes.get(field.key)
            )

        return JSONRenderer().render(json_object)
