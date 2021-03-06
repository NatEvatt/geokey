import factory

from projects.tests.model_factories import ProjectF
from users.tests.model_factories import UserF

from ..models import (
    Category, TextField, NumericField, DateTimeField,
    LookupField, LookupValue, Field, MultipleLookupField, MultipleLookupValue
)


class CategoryFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Category

    creator = factory.SubFactory(UserF)
    name = factory.Sequence(lambda n: "category %s" % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    project = factory.SubFactory(ProjectF)
    status = 'active'


class FieldFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Field

    name = factory.Sequence(lambda n: "field %s" % n)
    key = factory.Sequence(lambda n: "field_%s" % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    category = factory.SubFactory(CategoryFactory)
    status = 'active'
    required = False


class TextFieldFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = TextField

    name = factory.Sequence(lambda n: "textfield %s" % n)
    key = factory.Sequence(lambda n: "textfield_%s" % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    category = factory.SubFactory(CategoryFactory)
    status = 'active'
    required = False


class NumericFieldFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = NumericField

    name = factory.Sequence(lambda n: "numericfield %s" % n)
    key = factory.Sequence(lambda n: "numericfield_%s" % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    category = factory.SubFactory(CategoryFactory)
    status = 'active'
    required = False


class DateTimeFieldFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = DateTimeField

    name = factory.Sequence(lambda n: "datetimefield %s" % n)
    key = factory.Sequence(lambda n: "datetimefield_%s" % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    category = factory.SubFactory(CategoryFactory)
    status = 'active'
    required = False


class LookupFieldFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = LookupField

    name = factory.Sequence(lambda n: "lookupfield %s" % n)
    key = factory.Sequence(lambda n: "lookupfield_%s" % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    category = factory.SubFactory(CategoryFactory)
    status = 'active'
    required = False


class LookupValueFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = LookupValue

    name = factory.Sequence(lambda n: "lookupfield %s" % n)
    field = factory.SubFactory(LookupFieldFactory)
    status = 'active'


class MultipleLookupFieldFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = MultipleLookupField

    name = factory.Sequence(lambda n: "lookupfield %s" % n)
    key = factory.Sequence(lambda n: "lookupfield_%s" % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    category = factory.SubFactory(CategoryFactory)
    status = 'active'
    required = False


class MultipleLookupValueFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = MultipleLookupValue

    name = factory.Sequence(lambda n: "lookupfield %s" % n)
    field = factory.SubFactory(MultipleLookupFieldFactory)
    status = 'active'
