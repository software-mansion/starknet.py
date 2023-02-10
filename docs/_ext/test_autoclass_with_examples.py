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

    _append_hint(C.meth, C, " hint")
    _append_hint(E.meth, E, " hint")
    assert C.meth.__doc__ == "Docstring A hint"
    assert E.meth.__doc__ == "Docstring A hint"
