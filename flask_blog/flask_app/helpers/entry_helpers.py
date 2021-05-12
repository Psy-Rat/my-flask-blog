from flask import render_template, request

PAGINATION = 5


def pagination_sanitization(page):
    if page is not None and page.isdigit():
        page = int(page)
    else:
        page = 1
    return page


def render_paginated(template_name, query, paginate_by=PAGINATION, **context):
    '''
        Paginate query by flask. Returns rendered template with items after pagination.

    '''
    page = request.args.get('page')
    page = pagination_sanitization(page)

    if query is not None:
        object_list = query.paginate(page, paginate_by)
    else:
        object_list = None

    return render_template(
        template_name,
        object_list=object_list,
        **context)
