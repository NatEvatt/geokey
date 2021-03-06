from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from django.core import mail

from nose.tools import raises

from datagroupings.tests.model_factories import GroupingFactory
from users.tests.model_factories import (
    UserF, UserGroupF, GroupingUserGroupFactory
)

from .model_factories import ProjectF
from ..models import Project, Admins


class CreateProjectTest(TestCase):
    def test_create_project(self):
        creator = UserF.create()

        project = Project.create(
            'Test', 'Test desc', True, True, creator
        )
        self.assertIn(creator, project.admins.all())


class ProjectTest(TestCase):
    @raises(Project.DoesNotExist)
    def test_delete_project(self):
        project = ProjectF.create()
        project.delete()
        Project.objects.get(pk=project.id)

    def test_str(self):
        project = ProjectF.create(**{
            'name': 'Name',
            'status': 'inactive',
            'isprivate': False
        })
        self.assertEqual(
            str(project),
            'Name status: inactive private: False'
        )


class PrivateProjectTest(TestCase):
    def setUp(self):
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'isprivate': True,
            'everyone_contributes': False
        })

        self.view = GroupingFactory(
            **{'project': self.project, 'isprivate': True}
        )
        self.moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.project,
                'can_moderate': True
            })
        self.contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.project,
                'can_contribute': True
            })
        self.viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False
            })

        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': self.moderators_view})
        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': self.contributors_view})
        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': self.viewers_view})

        self.moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.project,
                'can_moderate': True
            })
        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.project,
                'can_contribute': True
            })
        self.viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False
            })

    def test_is_admin(self):
        self.assertTrue(self.project.is_admin(self.project.creator))

        self.assertFalse(self.project.is_admin(self.moderator_view))
        self.assertFalse(self.project.is_admin(self.moderator))

        self.assertFalse(self.project.is_admin(self.contributor_view))
        self.assertFalse(self.project.is_admin(self.contributor))

        self.assertFalse(self.project.is_admin(self.viewer_view))
        self.assertFalse(self.project.is_admin(self.viewer))

        self.assertFalse(self.project.is_admin(self.some_dude))
        self.assertFalse(self.project.is_admin(AnonymousUser()))

    def test_can_access(self):
        self.assertTrue(self.project.can_access(self.project.creator))

        self.assertTrue(self.project.can_access(self.moderator_view))
        self.assertTrue(self.project.can_access(self.moderator))

        self.assertTrue(self.project.can_access(self.contributor_view))
        self.assertTrue(self.project.can_access(self.contributor))

        self.assertTrue(self.project.can_access(self.viewer_view))
        self.assertFalse(self.project.can_access(self.viewer))

        self.assertFalse(self.project.can_access(self.some_dude))
        self.assertFalse(self.project.can_access(AnonymousUser()))

    def can_contribute(self):
        self.assertTrue(self.project.can_contribute(
            self.project.creator))

        self.assertTrue(self.project.can_contribute(self.moderator_view))
        self.assertTrue(self.project.can_contribute(self.moderator))

        self.assertTrue(self.project.can_contribute(self.contributor_view))
        self.assertTrue(self.project.can_contribute(self.contributor))

        self.assertFalse(self.project.can_contribute(self.viewer_view))
        self.assertFalse(self.project.can_contribute(self.viewer))

        self.assertFalse(self.project.can_contribute(self.some_dude))
        self.assertFalse(self.project.can_contribute(AnonymousUser()))

    def can_moderate(self):
        self.assertTrue(self.project.can_moderate(self.project.creator))

        self.assertTrue(self.project.can_moderate(self.moderator_view))
        self.assertTrue(self.project.can_moderate(self.moderator))

        self.assertFalse(self.project.can_moderate(self.contributor_view))
        self.assertFalse(self.project.can_moderate(self.contributor))

        self.assertFalse(self.project.can_moderate(self.viewer_view))
        self.assertFalse(self.project.can_moderate(self.viewer))

        self.assertFalse(self.project.can_moderate(self.some_dude))
        self.assertFalse(self.project.can_moderate(AnonymousUser()))

    def is_involved(self):
        self.assertTrue(self.project.is_involved(self.project.creator))

        self.assertTrue(self.project.is_involved(self.moderator_view))
        self.assertTrue(self.project.is_involved(self.moderator))

        self.assertTrue(self.project.is_involved(self.contributor_view))
        self.assertTrue(self.project.is_involved(self.contributor))

        self.assertTrue(self.project.is_involved(self.viewer_view))
        self.assertTrue(self.project.is_involved(self.viewer))

        self.assertFalse(self.project.is_involved(self.some_dude))
        self.assertFalse(self.project.is_involved(AnonymousUser()))


class PrivateProjectTest_PublicView(TestCase):
    def setUp(self):
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'isprivate': True,
            'everyone_contributes': False
        })

        self.view = GroupingFactory(
            **{'project': self.project, 'isprivate': False}
        )
        self.moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.project,
                'can_moderate': True
            })
        self.contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.project,
                'can_contribute': True
            })
        self.viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False
            })

        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': self.moderators_view})
        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': self.contributors_view})
        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': self.viewers_view})

        self.moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.project,
                'can_moderate': True
            })
        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.project,
                'can_contribute': True
            })
        self.viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False
            })

    def test_is_admin(self):
        self.assertTrue(self.project.is_admin(self.project.creator))

        self.assertFalse(self.project.is_admin(self.moderator_view))
        self.assertFalse(self.project.is_admin(self.moderator))

        self.assertFalse(self.project.is_admin(self.contributor_view))
        self.assertFalse(self.project.is_admin(self.contributor))

        self.assertFalse(self.project.is_admin(self.viewer_view))
        self.assertFalse(self.project.is_admin(self.viewer))

        self.assertFalse(self.project.is_admin(self.some_dude))
        self.assertFalse(self.project.is_admin(AnonymousUser()))

    def test_can_access(self):
        self.assertTrue(self.project.can_access(self.project.creator))

        self.assertTrue(self.project.can_access(self.moderator_view))
        self.assertTrue(self.project.can_access(self.moderator))

        self.assertTrue(self.project.can_access(self.contributor_view))
        self.assertTrue(self.project.can_access(self.contributor))

        self.assertTrue(self.project.can_access(self.viewer_view))
        self.assertFalse(self.project.can_access(self.viewer))

        self.assertFalse(self.project.can_access(self.some_dude))
        self.assertFalse(self.project.can_access(AnonymousUser()))

    def can_contribute(self):
        self.assertTrue(self.project.can_contribute(self.project.creator))

        self.assertTrue(self.project.can_contribute(self.moderator_view))
        self.assertTrue(self.project.can_contribute(self.moderator))

        self.assertTrue(self.project.can_contribute(self.contributor_view))
        self.assertTrue(self.project.can_contribute(self.contributor))

        self.assertFalse(self.project.can_contribute(self.viewer_view))
        self.assertFalse(self.project.can_contribute(self.viewer))

        self.assertFalse(self.project.can_contribute(self.some_dude))
        self.assertFalse(self.project.can_contribute(AnonymousUser()))

    def can_moderate(self):
        self.assertTrue(self.project.can_moderate(self.project.creator))

        self.assertTrue(self.project.can_moderate(self.moderator_view))
        self.assertTrue(self.project.can_moderate(self.moderator))

        self.assertFalse(self.project.can_moderate(self.contributor_view))
        self.assertFalse(self.project.can_moderate(self.contributor))

        self.assertFalse(self.project.can_moderate(self.viewer_view))
        self.assertFalse(self.project.can_moderate(self.viewer))

        self.assertFalse(self.project.can_moderate(self.some_dude))
        self.assertFalse(self.project.can_moderate(AnonymousUser()))

    def is_involved(self):
        self.assertTrue(self.project.is_involved(self.project.creator))

        self.assertTrue(self.project.is_involved(self.moderator_view))
        self.assertTrue(self.project.is_involved(self.moderator))

        self.assertTrue(self.project.is_involved(self.contributor_view))
        self.assertTrue(self.project.is_involved(self.contributor))

        self.assertTrue(self.project.is_involved(self.viewer_view))
        self.assertTrue(self.project.is_involved(self.viewer))

        self.assertFalse(self.project.is_involved(self.some_dude))
        self.assertFalse(self.project.is_involved(AnonymousUser()))


class PublicProjectTest(TestCase):
    def setUp(self):
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'isprivate': False,
            'everyone_contributes': False
        })

        self.view = GroupingFactory(
            **{'project': self.project, 'isprivate': True}
        )
        self.moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.project,
                'can_moderate': True
            })
        self.contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.project,
                'can_contribute': True
            })
        self.viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False
            })

        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': self.moderators_view})
        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': self.contributors_view})
        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': self.viewers_view})

        self.moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.project,
                'can_moderate': True
            })
        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.project,
                'can_contribute': True
            })
        self.viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False
            })

    def test_is_admin(self):
        self.assertTrue(self.project.is_admin(self.project.creator))

        self.assertFalse(self.project.is_admin(self.moderator_view))
        self.assertFalse(self.project.is_admin(self.moderator))

        self.assertFalse(self.project.is_admin(self.contributor_view))
        self.assertFalse(self.project.is_admin(self.contributor))

        self.assertFalse(self.project.is_admin(self.viewer_view))
        self.assertFalse(self.project.is_admin(self.viewer))

        self.assertFalse(self.project.is_admin(self.some_dude))
        self.assertFalse(self.project.is_admin(AnonymousUser()))

    def test_can_access(self):
        self.assertTrue(self.project.can_access(self.project.creator))

        self.assertTrue(self.project.can_access(self.moderator_view))
        self.assertTrue(self.project.can_access(self.moderator))

        self.assertTrue(self.project.can_access(self.contributor_view))
        self.assertTrue(self.project.can_access(self.contributor))

        self.assertTrue(self.project.can_access(self.viewer_view))
        self.assertFalse(self.project.can_access(self.viewer))

        self.assertFalse(self.project.can_access(self.some_dude))
        self.assertFalse(self.project.can_access(AnonymousUser()))

    def can_contribute(self):
        self.assertTrue(self.project.can_contribute(self.project.creator))

        self.assertTrue(self.project.can_contribute(self.moderator_view))
        self.assertTrue(self.project.can_contribute(self.moderator))

        self.assertTrue(self.project.can_contribute(self.contributor_view))
        self.assertTrue(self.project.can_contribute(self.contributor))

        self.assertFalse(self.project.can_contribute(self.viewer_view))
        self.assertFalse(self.project.can_contribute(self.viewer))

        self.assertFalse(self.project.can_contribute(self.some_dude))
        self.assertFalse(self.project.can_contribute(AnonymousUser()))

    def can_moderate(self):
        self.assertTrue(self.project.can_moderate(self.project.creator))

        self.assertTrue(self.project.can_moderate(self.moderator_view))
        self.assertTrue(self.project.can_moderate(self.moderator))

        self.assertFalse(self.project.can_moderate(self.contributor_view))
        self.assertFalse(self.project.can_moderate(self.contributor))

        self.assertFalse(self.project.can_moderate(self.viewer_view))
        self.assertFalse(self.project.can_moderate(self.viewer))

        self.assertFalse(self.project.can_moderate(self.some_dude))
        self.assertFalse(self.project.can_moderate(AnonymousUser()))

    def is_involved(self):
        self.assertTrue(self.project.is_involved(self.project.creator))

        self.assertTrue(self.project.is_involved(self.moderator_view))
        self.assertTrue(self.project.is_involved(self.moderator))

        self.assertTrue(self.project.is_involved(self.contributor_view))
        self.assertTrue(self.project.is_involved(self.contributor))

        self.assertTrue(self.project.is_involved(self.viewer_view))
        self.assertTrue(self.project.is_involved(self.viewer))

        self.assertFalse(self.project.is_involved(self.some_dude))
        self.assertFalse(self.project.is_involved(AnonymousUser()))


class PublicProjectTest_PublicView(TestCase):
    def setUp(self):
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'isprivate': False,
            'everyone_contributes': False
        })

        self.view = GroupingFactory(
            **{'project': self.project, 'isprivate': False}
        )
        self.moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.project,
                'can_moderate': True
            })
        self.contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.project,
                'can_contribute': True
            })
        self.viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False
            })

        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': self.moderators_view})
        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': self.contributors_view})
        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': self.viewers_view})

        self.moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.project,
                'can_moderate': True
            })
        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.project,
                'can_contribute': True
            })
        self.viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False
            })

    def test_is_admin(self):
        self.assertTrue(self.project.is_admin(self.project.creator))

        self.assertFalse(self.project.is_admin(self.moderator_view))
        self.assertFalse(self.project.is_admin(self.moderator))

        self.assertFalse(self.project.is_admin(self.contributor_view))
        self.assertFalse(self.project.is_admin(self.contributor))

        self.assertFalse(self.project.is_admin(self.viewer_view))
        self.assertFalse(self.project.is_admin(self.viewer))

        self.assertFalse(self.project.is_admin(self.some_dude))
        self.assertFalse(self.project.is_admin(AnonymousUser()))

    def test_can_access(self):
        self.assertTrue(self.project.can_access(self.project.creator))

        self.assertTrue(self.project.can_access(self.moderator_view))
        self.assertTrue(self.project.can_access(self.moderator))

        self.assertTrue(self.project.can_access(self.contributor_view))
        self.assertTrue(self.project.can_access(self.contributor))

        self.assertTrue(self.project.can_access(self.viewer_view))
        self.assertTrue(self.project.can_access(self.viewer))

        self.assertTrue(self.project.can_access(self.some_dude))
        self.assertTrue(self.project.can_access(AnonymousUser()))

    def can_contribute(self):
        self.assertTrue(self.project.can_contribute(self.project.creator))

        self.assertTrue(self.project.can_contribute(self.moderator_view))
        self.assertTrue(self.project.can_contribute(self.moderator))

        self.assertTrue(self.project.can_contribute(self.contributor_view))
        self.assertTrue(self.project.can_contribute(self.contributor))

        self.assertFalse(self.project.can_contribute(self.viewer_view))
        self.assertFalse(self.project.can_contribute(self.viewer))

        self.assertFalse(self.project.can_contribute(self.some_dude))
        self.assertFalse(self.project.can_contribute(AnonymousUser()))

    def can_moderate(self):
        self.assertTrue(self.project.can_moderate(self.project.creator))

        self.assertTrue(self.project.can_moderate(self.moderator_view))
        self.assertTrue(self.project.can_moderate(self.moderator))

        self.assertFalse(self.project.can_moderate(self.contributor_view))
        self.assertFalse(self.project.can_moderate(self.contributor))

        self.assertFalse(self.project.can_moderate(self.viewer_view))
        self.assertFalse(self.project.can_moderate(self.viewer))

        self.assertFalse(self.project.can_moderate(self.some_dude))
        self.assertFalse(self.project.can_moderate(AnonymousUser()))

    def is_involved(self):
        self.assertTrue(self.project.is_involved(self.project.creator))

        self.assertTrue(self.project.is_involved(self.moderator_view))
        self.assertTrue(self.project.is_involved(self.moderator))

        self.assertTrue(self.project.is_involved(self.contributor_view))
        self.assertTrue(self.project.is_involved(self.contributor))

        self.assertTrue(self.project.is_involved(self.viewer_view))
        self.assertTrue(self.project.is_involved(self.viewer))

        self.assertFalse(self.project.is_involved(self.some_dude))
        self.assertFalse(self.project.is_involved(AnonymousUser()))


class ProjectContactAdminsTest(TestCase):
    def test_all_contacts(self):
        admin = UserF.create()
        contributor = UserF.create()
        email_user = UserF.create()

        project = ProjectF.create(
            add_admins=[admin],
            add_contributors=[contributor]
        )

        project.contact_admins(email_user, 'Test email')
        # Should be 2 because project creator is admin too
        self.assertEquals(len(mail.outbox), 2)

    def test_selected_contacts(self):
        admin = UserF.create()
        contributor = UserF.create()
        email_user = UserF.create()

        project = ProjectF.create(
            add_admins=[admin],
            add_contributors=[contributor]
        )

        admin_rel = Admins.objects.get(project=project, user=admin)
        admin_rel.contact = False
        admin_rel.save()

        project.contact_admins(email_user, 'Test email')
        self.assertEquals(len(mail.outbox), 1)
