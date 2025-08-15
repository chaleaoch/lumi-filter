"""Pydantic schemas for the example API layer."""

from __future__ import annotations

import datetime
from pydantic import BaseModel, Field


class ProductIn(BaseModel):
	name: str = Field(..., max_length=120)
	price: float = Field(..., ge=0)
	is_active: bool = True


class ProductOut(ProductIn):
	id: int
	created_at: datetime.datetime

	class Config:
		from_attributes = True


class ProductListQuery(BaseModel):
	"""Query params for list endpoint (subset to demonstrate)"""

	# lumi_filter handles actual filtering; we just keep raw strings here
	name: str | None = None
	price__gte: float | None = None
	price__lte: float | None = None
	is_active: bool | None = None
	ordering: str | None = None  # e.g. "-price,name"

