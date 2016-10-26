import morepath
from more.pathtool.main import get_path_and_view_info, format_text, format_csv
from io import BytesIO


def restrict(infos, names):
    result = []
    for info in infos:
        d = {}
        for name in names:
            try:
                d[name] = info[name]
            except KeyError:
                pass
        result.append(d)
    return result


def test_one_app():
    class App(morepath.App):
        pass

    class A(object):
        pass

    @App.path(path='/foo', model=A)
    def get_a():
        return A()

    App.commit()

    infos = get_path_and_view_info(App)
    infos = restrict(infos, ['path', 'directive'])
    assert infos == [{'path': '/foo', 'directive': 'path'}]


def test_app_variables():
    class App(morepath.App):
        pass

    class A(object):
        pass

    @App.path(path='/users/{id}', model=A)
    def get_a(id):
        return A()

    App.commit()

    infos = get_path_and_view_info(App)
    infos = restrict(infos, ['path', 'directive'])
    assert infos == [{'path': '/users/{id}', 'directive': 'path'}]


def test_mounted_app_paths_only():
    class App(morepath.App):
        pass

    class A(object):
        pass

    @App.path(path='foo', model=A)
    def get_a():
        return A()

    class Sub(morepath.App):
        pass

    class B(object):
        pass

    @Sub.path(path='bar', model=B)
    def get_b():
        return B()

    @App.mount(path='sub', app=Sub)
    def get_sub():
        return Sub()

    App.commit()

    infos = get_path_and_view_info(App)
    infos = restrict(infos, ['path', 'directive'])

    assert infos == [
        {'path': '/foo', 'directive': 'path'},
        {'path': '/sub', 'directive': 'mount'},
        {'path': '/sub/bar', 'directive': 'path'}
    ]


def test_one_app_view_actions():
    class App(morepath.App):
        pass

    class A(object):
        pass

    @App.path(path='/foo', model=A)
    def get_a():
        return A()

    @App.view(model=A)
    def a_default(self, request):
        return ""

    App.commit()

    infos = get_path_and_view_info(App)
    infos = restrict(infos, ['path', 'directive'])

    assert infos == [
        {'path': '/foo', 'directive': 'path'},
        {'path': '/foo', 'directive': 'view'},
    ]


def test_one_app_named_view():
    class App(morepath.App):
        pass

    class A(object):
        pass

    @App.path(path='/foo', model=A)
    def get_a():
        return A()

    @App.view(model=A)
    def a_default(self, request):
        return ""

    @App.view(model=A, name='edit')
    def a_edit(self, request):
        return ""

    App.commit()

    infos = get_path_and_view_info(App)
    infos = restrict(infos, ['path', 'directive'])

    assert infos == [
        {'path': '/foo', 'directive': 'path'},
        {'path': '/foo', 'directive': 'view'},
        {'path': '/foo/+edit', 'directive': 'view'},
    ]


def test_one_app_view_predicates():
    class App(morepath.App):
        pass

    class A(object):
        pass

    @App.path(path='/foo', model=A)
    def get_a():
        return A()

    @App.view(model=A)
    def a_default(self, request):
        return ""

    @App.view(model=A, name='edit')
    def a_edit(self, request):
        return ""

    App.commit()

    infos = get_path_and_view_info(App)

    predicates = [d.get('predicates') for d in infos if 'predicates' in d]

    assert predicates == [{}, {'name': 'edit'}]


def test_one_app_view_actions_base_class():
    class App(morepath.App):
        pass

    class Base(object):
        pass

    class A(Base):
        pass

    @App.path(path='/foo', model=A)
    def get_a():
        return A()

    @App.view(model=Base)
    def base_default(self, request):
        return ""

    App.commit()

    infos = get_path_and_view_info(App)
    infos = restrict(infos, ['path', 'directive'])

    assert infos == [
        {'path': '/foo', 'directive': 'path'},
        {'path': '/foo', 'directive': 'view'},
    ]


def test_mounted_app_paths_and_views():
    class App(morepath.App):
        pass

    class A(object):
        pass

    @App.path(path='foo', model=A)
    def get_a():
        return A()

    @App.json(model=A)
    def a_default(self, request):
        pass

    class Sub(morepath.App):
        pass

    class B(object):
        pass

    @Sub.path(path='bar', model=B)
    def get_b():
        return B()

    @Sub.view(model=B)
    def b_default(self, request):
        return ''

    # shouldn't be picked up as it's in Sub
    @Sub.view(model=A)
    def a_sub_view(self, request):
        return ''

    @App.mount(path='sub', app=Sub)
    def get_sub():
        return Sub()

    App.commit()

    infos = get_path_and_view_info(App)
    infos = restrict(infos, ['path', 'directive'])

    assert infos == [
        {'path': '/foo', 'directive': 'path'},
        {'path': '/foo', 'directive': 'json'},
        {'path': '/sub', 'directive': 'mount'},
        {'path': '/sub/bar', 'directive': 'path'},
        {'path': '/sub/bar', 'directive': 'view'}
    ]


def test_format_text():
    infos = [
        {
            'path': '/foo',
            'directive': 'path',
            'filelineno': 'flurb',
        },
        {
            'path': '/muchlonger',
            'directive': 'path',
            'filelineno': 'flurb2',
        }
    ]
    f = BytesIO()
    format_text(f, infos)

    s = f.getvalue()
    assert s == '''\
/foo        path flurb
/muchlonger path flurb2
'''
