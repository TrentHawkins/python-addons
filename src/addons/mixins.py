from __future__ import annotations


import typing

from . import protocols


class Boolean(protocols.Boolean):

	def __or__(self, other: typing.Self, /) -> typing.Self:
		return ~(self & ~other)

	def __sub__(self, other: typing.Self, /) -> typing.Self:
		return self & ~other

	def __xor__(self, other: typing.Self, /) -> typing.Self:
		return (self & ~other) | (~self & other)
	#	return (self |  other) - ( self & other)


class AddGroup(protocols.AddGroup):

	def __sub__(self, other: typing.Self, /) -> typing.Self:
		return self + -other
