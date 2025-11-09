"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryFilters(BaseModel):
    service: Optional[str] = None
    severity: Optional[str] = None
    keywords: Optional[List[str]] = None


class InsightRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    filters: QueryFilters = Field(default_factory=QueryFilters)
    question: Optional[str] = None


class InsightResponse(BaseModel):
    summary: str
    cause: str
    remediation: List[str]
    severity: str
    follow_up_queries: List[str] = Field(default_factory=list)
    raw_logs: List[Dict[str, Any]] = Field(default_factory=list)


class AlertPayload(BaseModel):
    alarm_name: str
    state: str
    detail: Dict[str, Any]


class AlertResponse(BaseModel):
    markdown: str
    severity: str
    dashboard_links: List[str]
