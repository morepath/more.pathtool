import sys
import morepath
from more.pathtool.main import (
    get_path_and_view_info, format_text, format_csv, dotted_name)
from io import StringIO, BytesIO

PY3 = not sys.version_info[0] < 3


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
            'path': u'/foo',
            'directive': u'path',
            'filelineno': u'flurb',
        },
        {
            'path': u'/muchlonger',
            'directive': u'path',
            'filelineno': u'flurb2',
        }
    ]
    f = StringIO()
    format_text(f, infos)

    s = f.getvalue()
    assert s == '''\
/foo        path flurb
/muchlonger path flurb2
'''


def io():
    if PY3:
        return StringIO()
    else:
        return BytesIO()


def test_format_csv():
    infos = [
        {
            u'path': u'/foo',
            u'directive': u'path',
            u'filename': u'flurb.py',
            u'lineno': 17,
        },
        {
            u'path': u'/muchlonger',
            u'directive': u'path',
            u'filename': u'flurb2.py',
            u'lineno': 28,
        },
        {
            u'path': u'/muchlonger/+edit',
            u'directive': u'view',
            u'filename': u'flurb3.py',
            u'lineno': 1,
            u'permission': 'public',
            u'view_name': 'edit',
        },
        {
            u'path': u'internal',
            u'directive': u'view',
            u'filename': u'flurb3.py',
            u'lineno': 4,
            u'permission': 'internal',
            u'view_name': 'something',
        }
    ]
    f = io()
    format_csv(f, infos)

    s = f.getvalue()
    assert s == '''\
path,directive,filename,lineno,model,permission,view_name,request_method,extra_predicates\r
/foo,path,flurb.py,17,,,,,\r
/muchlonger,path,flurb2.py,28,,,,,\r
/muchlonger/+edit,view,flurb3.py,1,,public,edit,,\r
internal,view,flurb3.py,4,,internal,something,,\r
'''


def test_one_app_with_text_format():
    class App(morepath.App):
        pass

    class A(object):
        pass

    @App.path(path='/foo', model=A)
    def get_a():
        return A()

    App.commit()

    infos = get_path_and_view_info(App)

    infos[0]['filelineno'] = 'File /fake.py, line 335'
    f = StringIO()
    format_text(f, infos)

    s = f.getvalue()
    assert s == '''\
/foo path File /fake.py, line 335
'''


def test_one_app_with_csv_format():
    class App(morepath.App):
        pass

    class A(object):
        pass

    @App.path(path='/foo', model=A)
    def get_a():
        return A()

    App.commit()

    infos = get_path_and_view_info(App)

    infos[0]['filename'] = 'flurb.py'
    infos[0]['lineno'] = 17

    f = io()
    format_csv(f, infos)

    s = f.getvalue()
    assert s == '''\
path,directive,filename,lineno,model,permission,view_name,request_method,extra_predicates\r
/foo,path,flurb.py,17,test_path_tool.A,,,,\r
'''


def test_name_and_request_method():
    class App(morepath.App):
        pass

    class A(object):
        pass

    @App.path(path='/foo', model=A)
    def get_a():
        return A()

    @App.view(model=A, name='edit', request_method='POST')
    def a_default(self, request):
        return "default"

    App.commit()

    infos = get_path_and_view_info(App)

    infos[0]['filename'] = 'flurb.py'
    infos[0]['lineno'] = 17

    infos[1]['filename'] = 'flurb.py'
    infos[1]['lineno'] = 20

    f = io()
    format_csv(f, infos)

    s = f.getvalue()
    assert s == '''\
path,directive,filename,lineno,model,permission,view_name,request_method,extra_predicates\r
/foo,path,flurb.py,17,test_path_tool.A,,,,\r
/foo/+edit,view,flurb.py,20,test_path_tool.A,public,edit,POST,\r
'''


def test_extra_predicates():
    class App(morepath.App):
        pass

    class A(object):
        pass

    class B(object):
        pass

    @App.path(path='/foo', model=A)
    def get_a():
        return A()

    @App.view(model=A, body_model=B, request_method='POST')
    def post_a(self, request):
        return A()

    App.commit()

    infos = get_path_and_view_info(App)

    for info in infos:
        info['filename'] = 'flurb.py'
        info['lineno'] = 17

    f = io()
    format_csv(f, infos)

    s = f.getvalue()
    assert s == '''\
path,directive,filename,lineno,model,permission,view_name,request_method,extra_predicates\r
/foo,path,flurb.py,17,test_path_tool.A,,,,\r
/foo,view,flurb.py,17,test_path_tool.A,public,,POST,y\r
'''


def test_internal_view():
    class App(morepath.App):
        pass

    class A(object):
        pass

    @App.path(path='/foo', model=A)
    def get_a():
        return A()

    @App.view(model=A, name='bar', internal=True)
    def a_default(self, request):
        return "default"

    App.commit()

    infos = get_path_and_view_info(App)

    infos[0]['filename'] = 'flurb.py'
    infos[0]['lineno'] = 17

    infos[1]['filename'] = 'flurb.py'
    infos[1]['lineno'] = 20

    f = io()
    format_csv(f, infos)

    s = f.getvalue()
    assert s == '''\
path,directive,filename,lineno,model,permission,view_name,request_method,extra_predicates\r
/foo,path,flurb.py,17,test_path_tool.A,,,,\r
internal,view,flurb.py,20,test_path_tool.A,internal,bar,GET,\r
'''


def test_absorb():
    class App(morepath.App):
        pass

    class A(object):
        pass

    @App.path(path='/foo', model=A, absorb=True)
    def get_a():
        return A()

    App.commit()

    infos = get_path_and_view_info(App)

    infos[0]['filename'] = 'flurb.py'
    infos[0]['lineno'] = 17

    f = io()
    format_csv(f, infos)

    s = f.getvalue()
    assert s == '''\
path,directive,filename,lineno,model,permission,view_name,request_method,extra_predicates\r
/foo/...,path,flurb.py,17,test_path_tool.A,,,,\r
'''


def test_sort_paths_and_views():
    class App(morepath.App):
        pass

    class A(object):
        pass

    class B(object):
        pass

    @App.path(path='/a', model=A)
    def get_a():
        return A()

    @App.path(path='/b', model=B)
    def get_b():
        return B()

    @App.view(model=A)
    def a_default(self, request):
        return "default"

    @App.view(model=A, name='x')
    def a_x(self, request):
        return "x"

    @App.view(model=A, name='y')
    def a_y(self, request):
        return "y"

    @App.view(model=A, name='y', request_method='POST')
    def a_y_post(self, request):
        return 'y'

    @App.view(model=A, name='y', request_method='PUT')
    def a_y_put(self, request):
        return 'y'

    @App.view(model=A, name='y', request_method='DELETE')
    def a_y_delete(self, request):
        return 'y'

    @App.view(model=A, name='z')
    def a_z(self, request):
        return 'y'

    @App.view(model=A, name='i', internal=True)
    def a_internal(self, request):
        return 'i'

    @App.view(model=B)
    def b_default(self, request):
        return 'b'

    App.commit()

    infos = get_path_and_view_info(App)

    for info in infos:
        info['filename'] = 'flurb.py'
        info['lineno'] = 17

    f = io()
    format_csv(f, infos)

    s = f.getvalue()
    assert s == '''\
path,directive,filename,lineno,model,permission,view_name,request_method,extra_predicates\r
/a,path,flurb.py,17,test_path_tool.A,,,,\r
/a,view,flurb.py,17,test_path_tool.A,public,,GET,\r
internal,view,flurb.py,17,test_path_tool.A,internal,i,GET,\r
/a/+x,view,flurb.py,17,test_path_tool.A,public,x,GET,\r
/a/+y,view,flurb.py,17,test_path_tool.A,public,y,DELETE,\r
/a/+y,view,flurb.py,17,test_path_tool.A,public,y,GET,\r
/a/+y,view,flurb.py,17,test_path_tool.A,public,y,POST,\r
/a/+y,view,flurb.py,17,test_path_tool.A,public,y,PUT,\r
/a/+z,view,flurb.py,17,test_path_tool.A,public,z,GET,\r
/b,path,flurb.py,17,test_path_tool.B,,,,\r
/b,view,flurb.py,17,test_path_tool.B,public,,GET,\r
'''


def test_dotted_name():
    from morepath.directive import ViewAction
    assert dotted_name(ViewAction) == 'morepath.directive.ViewAction'


def test_defer_doesnt_break_tool():
    class App(morepath.App):
        pass

    class Sub(morepath.App):
        pass

    class A(object):
        pass

    @App.path(path='/foo', model=A)
    def get_a():
        return A()

    @App.mount(path='/sub', app=Sub)
    def get_sub():
        return Sub()

    @Sub.defer_links(model=A)
    def defer_a(app, obj):
        return app.parent

    App.commit()

    infos = get_path_and_view_info(App)
    infos = restrict(infos, ['path', 'directive'])

    assert infos == [
        {'path': '/foo', 'directive': 'path'},
        {'path': '/sub', 'directive': 'mount'}
    ]


def test_permissions():
    class App(morepath.App):
        pass

    class A(object):
        pass

    @App.path(path='/foo', model=A)
    def get_a():
        return A()

    class ReadPermission(object):
        pass

    @App.view(model=A, permission=ReadPermission)
    def a_default(self, request):
        pass

    App.commit()

    infos = get_path_and_view_info(App)

    for info in infos:
        info['filename'] = 'flurb.py'
        info['lineno'] = 17

    f = io()
    format_csv(f, infos)

    s = f.getvalue()
    assert s == '''\
path,directive,filename,lineno,model,permission,view_name,request_method,extra_predicates\r
/foo,path,flurb.py,17,test_path_tool.A,,,,\r
/foo,view,flurb.py,17,test_path_tool.A,test_path_tool.ReadPermission,,GET,\r
'''
