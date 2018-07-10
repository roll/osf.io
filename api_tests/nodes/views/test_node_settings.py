
# -*- coding: utf-8 -*-
import pytest
from framework.auth import Auth
from api.base.settings.defaults import API_BASE
from osf_tests.factories import (
    AuthUserFactory,
    ProjectFactory,
)


@pytest.mark.django_db
class TestNodeSettingsUpdate:

    @pytest.fixture()
    def admin_contrib(self):
        return AuthUserFactory()

    @pytest.fixture()
    def write_contrib(self):
        return AuthUserFactory()

    @pytest.fixture()
    def read_contrib(self):
        return AuthUserFactory()

    @pytest.fixture()
    def project(self, admin_contrib, write_contrib, read_contrib):
        project = ProjectFactory(creator=admin_contrib)
        project.add_contributor(write_contrib, ['write', 'read'])
        project.add_contributor(read_contrib, ['read'])
        project.save()
        return project

    @pytest.fixture()
    def url(self, project):
        return '/{}nodes/{}/settings/'.format(API_BASE, project._id)

    @pytest.fixture()
    def payload(self, project):
        return {
            'data': {
                'id': project._id,
                'type': 'node-settings',
                'attributes': {
                }
            }
        }

    def test_patch_permissions(self, app, project, payload, admin_contrib, write_contrib, read_contrib, url):
        payload['data']['attributes']['redirect_link_enabled'] = True
        payload['data']['attributes']['redirect_link_url'] = 'https://cos.io'
        # Logged out
        res = app.patch_json_api(url, payload, expect_errors=True)
        assert res.status_code == 401

        # Logged in, noncontrib
        noncontrib = AuthUserFactory()
        res = app.patch_json_api(url, payload, auth=noncontrib.auth, expect_errors=True)
        assert res.status_code == 403

        # Logged in read
        res = app.patch_json_api(url, payload, auth=read_contrib.auth, expect_errors=True)
        assert res.status_code == 403

        # Logged in write (Write contribs can only change some node settings)
        res = app.patch_json_api(url, payload, auth=write_contrib.auth, expect_errors=True)
        assert res.status_code == 200

        # Logged in admin
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth)
        assert res.status_code == 200

    def test_patch_invalid_type(self, app, project, payload, admin_contrib, url):
        payload['data']['type'] = 'Invalid Type'

        # Logged in admin
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth, expect_errors=True)
        assert res.status_code == 409

    def test_patch_access_requests_enabled(self, app, project, payload, admin_contrib, write_contrib, url):
        assert project.access_requests_enabled is True
        payload['data']['attributes']['access_requests_enabled'] = False

        # Write cannot modify this field
        res = app.patch_json_api(url, payload, auth=write_contrib.auth, expect_errors=True)
        assert res.status_code == 403

        # Logged in admin
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth)
        assert res.status_code == 200
        project.reload()
        assert project.access_requests_enabled is False

        payload['data']['attributes']['access_requests_enabled'] = True
        # Logged in admin
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth)
        assert res.status_code == 200
        project.reload()
        assert project.access_requests_enabled is True

    def test_patch_anyone_can_comment(self, app, project, payload, admin_contrib, write_contrib, url):
        assert project.comment_level == 'public'
        payload['data']['attributes']['anyone_can_comment'] = False

        # Write cannot modify this field
        res = app.patch_json_api(url, payload, auth=write_contrib.auth, expect_errors=True)
        assert res.status_code == 403

        # Logged in admin
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth)
        assert res.status_code == 200
        project.reload()
        assert project.comment_level == 'private'

        payload['data']['attributes']['anyone_can_comment'] = True
        # Logged in admin
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth)
        assert res.status_code == 200
        project.reload()
        assert project.comment_level == 'public'

    def test_patch_anyone_can_edit_wiki(self, app, project, payload, admin_contrib, write_contrib, url):
        project.is_public = True
        project.save()
        wiki_addon = project.get_addon('wiki')
        assert wiki_addon.is_publicly_editable is False
        payload['data']['attributes']['anyone_can_edit_wiki'] = True

        # Write cannot modify this field
        res = app.patch_json_api(url, payload, auth=write_contrib.auth, expect_errors=True)
        assert res.status_code == 403

        # Logged in admin
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth)
        assert res.status_code == 200
        wiki_addon.reload()
        assert wiki_addon.is_publicly_editable is True

        payload['data']['attributes']['anyone_can_edit_wiki'] = False
        # Logged in admin
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth)
        assert res.status_code == 200
        wiki_addon.reload()
        assert wiki_addon.is_publicly_editable is False

        # Test wiki disabled in same request so cannot change wiki_settings
        payload['data']['attributes']['wiki_enabled'] = False
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth, expect_errors=True)
        assert res.status_code == 400

        # Test wiki disabled so cannot change wiki settings
        project.delete_addon('wiki', Auth(admin_contrib))
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth, expect_errors=True)
        assert res.status_code == 400

        # Test wiki enabled so can change wiki settings
        payload['data']['attributes']['wiki_enabled'] = True
        payload['data']['attributes']['anyone_can_edit_wiki'] = True
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth, expect_errors=True)
        assert res.status_code == 200
        assert project.get_addon('wiki').is_publicly_editable is True

        # If project is private, cannot change settings to allow anyone to edit wiki
        project.is_public = False
        project.save()
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth, expect_errors=True)
        assert res.status_code == 400
        assert res.json['errors'][0]['detail'] == 'To allow all OSF users to edit the wiki, the project must be public.'

    def test_patch_wiki_enabled(self, app, project, payload, admin_contrib, write_contrib, url):
        assert project.get_addon('wiki') is not None
        payload['data']['attributes']['wiki_enabled'] = False

        # Write cannot modify this field
        res = app.patch_json_api(url, payload, auth=write_contrib.auth, expect_errors=True)
        assert res.status_code == 403

        # Logged in admin
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth)
        assert res.status_code == 200
        assert project.get_addon('wiki') is None

        # Nothing happens if attempting to disable an already-disabled wiki
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth)
        assert res.status_code == 200
        assert project.get_addon('wiki') is None

        payload['data']['attributes']['wiki_enabled'] = True
        # Logged in admin
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth)
        assert res.status_code == 200
        assert project.get_addon('wiki') is not None

        # Nothing happens if attempting to enable an already-enabled-wiki
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth)
        assert res.status_code == 200
        assert project.get_addon('wiki') is not None

    def test_redirect_link_enabled(self, app, project, payload, admin_contrib, write_contrib, url):
        assert project.get_addon('forward') is None
        payload['data']['attributes']['redirect_link_enabled'] = True

        # Redirect link not included
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth, expect_errors=True)
        assert res.status_code == 400
        assert res.json['errors'][0]['detail'] == 'You must include a redirect URL to enable a redirect.'

        payload['data']['attributes']['redirect_link_url'] = 'https://cos.io'
        payload['data']['attributes']['redirect_link_label'] = 'My Link'
        # Write contrib can modify forward related fields
        res = app.patch_json_api(url, payload, auth=write_contrib.auth)
        assert res.status_code == 200
        forward_addon = project.get_addon('forward')
        assert forward_addon is not None
        assert forward_addon.url == 'https://cos.io'
        assert forward_addon.label == 'My Link'

        # Attempting to set redirect_link_url when redirect_link not enabled
        payload['data']['attributes']['redirect_link_enabled'] = False
        del payload['data']['attributes']['redirect_link_label']
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth, expect_errors=True)
        assert res.status_code == 400
        assert res.json['errors'][0]['detail'] == 'You must first set redirect_link_enabled to True before specifying a redirect link URL.'

        # Attempting to set redirect_link_label when redirect_link not enabled
        payload['data']['attributes']['redirect_link_enabled'] = False
        del payload['data']['attributes']['redirect_link_url']
        payload['data']['attributes']['redirect_link_label'] = 'My Link'
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth, expect_errors=True)
        assert res.status_code == 400
        assert res.json['errors'][0]['detail'] == 'You must first set redirect_link_enabled to True before specifying a redirect link label.'

        payload['data']['attributes']['redirect_link_enabled'] = False
        del payload['data']['attributes']['redirect_link_label']
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth)
        assert res.status_code == 200
        forward_addon = project.get_addon('forward')
        assert forward_addon is None

    def test_redirect_link_label_char_limit(self, app, project, payload, admin_contrib, url):
        project.add_addon('forward', ())
        project.save()

        payload['data']['attributes']['redirect_link_label'] = 'a' * 52
        res = app.patch_json_api(url, payload, auth=admin_contrib.auth, expect_errors=True)
        assert res.status_code == 400
        assert res.json['errors'][0]['detail'] == 'Ensure this field has no more than 50 characters.'
