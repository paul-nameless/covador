import pytest

from covador import Int, Str, Bytes, split, enum


def test_int():
    assert Int()(10) == 10
    assert Int()(u'10') == 10
    assert Int()(b'10') == 10
    assert Int(16)(u'10') == 16
    assert Int(2)(b'10') == 2


def test_str():
    assert repr(Str()(u'aaa')) == repr(u'aaa')
    assert repr(Str()(b'aaa')) == repr(u'aaa')
    assert repr(Str(encoding=False)(b'aaa')) == repr(b'aaa')
    assert repr(Str()(10)) == repr('10')


def test_bytes():
    assert repr(Bytes()('aaa')) == repr(b'aaa')
    assert repr(Bytes()(b'aaa')) == repr(b'aaa')
    assert repr(Bytes()(10)) == repr(b'10')


def test_split():
    assert split()('aa, bb') == ['aa', 'bb']
    assert split(strip=False)('aa, bb') == ['aa', ' bb']
    assert split(int)('1, 3, 5') == [1, 3, 5]
    assert split(int)('1, 3, 5,,') == [1, 3, 5]
    assert split(int, separator=None)('1\t2') == [1, 2]


def test_enum():
    assert enum(1, 2)(1) == 1

    with pytest.raises(ValueError) as ei:
        enum(1, 2)(3)
    assert ei.value.message == '3 not in [1, 2]'

    assert enum(['boo', 'foo'])('boo') == 'boo'

    with pytest.raises(ValueError) as ei:
        enum(['boo', 'foo'])('bar')
    assert ei.value.message == "'bar' not in ['boo', 'foo']"


def test_split_enum():
    with pytest.raises(ValueError) as ei:
        print split(enum('boo', 'foo'))('boo, bar, foo')


    e = ei.value
    assert e.clean == ['boo', None, 'foo']
    assert len(e.errors) == 1
    assert e.errors[0][0] == 1
    assert e.errors[0][1].message == "'bar' not in ['boo', 'foo']"
