from docs._ext.autoclass_with_examples import _append_hint


def test_docstring_inheritance():
    class A:
        def meth(self):
            """Docstring A"""
            pass

    class B(A):
        def meth(self):
            pass

    class C(B):
        def meth(self):
            pass

    class D(A):
        pass

    class E(D):
        def meth(self):
            pass

    _append_hint("meth", C.meth, C.__base__, " hint")
    _append_hint("meth", E.meth, E.__base__, " hint")
    assert C.meth.__doc__ == "Docstring A hint"
    assert E.meth.__doc__ == "Docstring A hint"
