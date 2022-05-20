from __future__ import annotations
import numbers
import operator
from typing import Callable, FrozenSet, Iterable, Set, Union


class TaintInt(numbers.Integral):
    def __init__(self, value: Union[int, TaintInt], taint: Iterable[str] = []):
        self._value: int
        self._taint: FrozenSet[str]
        if isinstance(value, int):
            self._value = value
            self._taint = frozenset(taint)
        elif isinstance(value, TaintInt):
            self._value = int(value)
            self._taint = frozenset(taint).union(value.taint)
        else:
            raise Exception(f"Can't initialise TaintInt with value of type {type(value)}")

    @property
    def value(self) -> int:
        return self._value

    @property
    def taint(self) -> FrozenSet[str]:
        return self._taint

    def merge_taint(self, other):
        return self.taint.union(other.taint)

    def __key(self):
        # TODO: Temporarily unique based on value
        return self.value

    def __hash__(self):
        return hash(self.__key())

    def __int__(self):
        return self.value

    def __abs__(self):
        return TaintInt(abs(self.value), self.taint)

    def __repr__(self):
        return f"<TaintInt {self.value} {self.taint}>"

    def __format__(self, format_spec=None):
        return self.__repr__()

    def _operator_with_reverse(operator_func: Callable):
        def forward(a, b):
            lhs = a.value
            if isinstance(b, TaintInt):
                rhs = b.value
                taint = a.merge_taint(b)
            elif isinstance(b, int):
                rhs = b
                taint = a.taint
            else:
                return NotImplemented
            return TaintInt(operator_func(lhs, rhs), taint)

        forward.__name__ = "__" + operator_func.__name__ + "__"

        def reverse(b, a):
            rhs = b.value
            if isinstance(a, TaintInt):
                lhs = a.value
                taint = b.merge_taint(a)
            elif isinstance(a, int):
                lhs = a
                taint = b.taint
            else:
                return NotImplemented
            return TaintInt(operator_func(lhs, rhs), taint)

        reverse.__name__ = "__r" + operator_func.__name__ + "__"

        return forward, reverse

    def _operator(operator_func: Callable):
        def forward(a, b):
            lhs = a.value
            if isinstance(b, TaintInt):
                rhs = b.value
                taint = a.merge_taint(b)
            elif isinstance(b, int):
                rhs = b
                taint = a.taint
            else:
                return NotImplemented
            return TaintInt(operator_func(lhs, rhs), taint)

        forward.__name__ = "__" + operator_func.__name__ + "__"

        return forward

    def _operator_single(operator_func: Callable):
        def op(a):
            return TaintInt(operator_func(a.value), a.taint)

        op.__name__ = "__" + operator_func.__name__ + "__"

        return op

    __add__, __radd__ = _operator_with_reverse(operator.add)
    __sub__, __rsub__ = _operator_with_reverse(operator.sub)
    __mul__, __rmul__ = _operator_with_reverse(operator.mul)
    __mod__, __rmod__ = _operator_with_reverse(operator.mod)
    __truediv__, __rtruediv__ = _operator_with_reverse(operator.truediv)
    __floordiv__, __rfloordiv__ = _operator_with_reverse(operator.floordiv)
    __divmod__, __rdivmod__ = _operator_with_reverse(divmod)
    __and__, __rand__ = _operator_with_reverse(operator.and_)
    __or__, __ror__ = _operator_with_reverse(operator.or_)
    __xor__, __rxor__ = _operator_with_reverse(operator.xor)
    __lshift__, __rlshift__ = _operator_with_reverse(operator.lshift)
    __rshift__, __rrshift__ = _operator_with_reverse(operator.rshift)

    __le__ = _operator(operator.le)
    __lt__ = _operator(operator.lt)
    __ge__ = _operator(operator.ge)
    __gt__ = _operator(operator.gt)

    __neg__ = _operator_single(operator.neg)
    __invert__ = _operator_single(operator.invert)

    def __ceil__(self):
        raise NotImplementedError

    def __eq__(self, other):
        if isinstance(other, TaintInt):
            return self.value == other.value
        elif isinstance(other, int):
            return self.value == other

    def __floor__(self):
        raise NotImplementedError

    def __pos__(self):
        raise NotImplementedError

    def __pow__(self):
        raise NotImplementedError

    def __round__(self):
        raise NotImplementedError

    def __rpow__(self):
        raise NotImplementedError

    def __trunc__(self):
        raise NotImplementedError
