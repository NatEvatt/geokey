from django import template

register = template.Library()


def get_user_group(group, grouping):
    disabled = ''
    if not grouping.project.isprivate and not grouping.isprivate:
        disabled = 'disabled="disabled"'

    if grouping.usergroups.filter(usergroup=group).exists():
        html = '<div class="overview-list-item">\
                    <button type="button" name="%s" class="btn btn-default pull-right active grant-single" data-toggle="button" %s><span class="text-danger">Revoke access</span></button><strong>%s</strong><p>%s</p>\
                </div>' % (
            group.id,
            disabled,
            group.name,
            group.description
        )
    else:
        html = '<div class="overview-list-item">\
                    <button type="button" name="%s" class="btn btn-default pull-right grant-single" data-toggle="button" %s><span class="text-success">Grant access</span></button><strong>%s</strong><p>%s</p>\
                </div>' % (
            group.id,
            disabled,
            group.name,
            group.description
        )

    return html


@register.simple_tag
def usergroups(grouping):
    html = ''
    for group in grouping.project.usergroups.all():
        html += get_user_group(group, grouping)

    return html
