#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

@dataclass
class DataExtractionResult:
    """Result container for extracted data from a webpage"""
    url: str
    title: str
    text_content: str
    links: List[str]
    images: List[str]
    forms: List[Dict[str, str]]
    metadata: Dict[str, str]
    screenshot_path: Optional[str] = None
    html_content: Optional[str] = None
    status_code: Optional[int] = None
    error: Optional[str] = None

@dataclass
class NavigationResult:
    """Result container for navigation operations"""
    url: str
    success: bool
    final_url: str
    status_code: int
    error: Optional[str] = None
    redirect_count: int = 0
    load_time: float = 0.0

@dataclass
class FormSubmissionResult:
    """Result container for form submissions"""
    form_id: str
    success: bool
    response_url: str
    status_code: int
    error: Optional[str] = None
    submitted_data: Optional[Dict[str, str]] = None

@dataclass
class AutomationStep:
    """Single step in an automation sequence"""
    action: str
    selector: Optional[str] = None
    value: Optional[Union[str, int, float]] = None
    wait_time: float = 0.5
    screenshot: bool = False

@dataclass
class AutomationResult:
    """Result container for automation sequences"""
    steps_completed: int
    success: bool
    final_url: str
    error: Optional[str] = None
    screenshots: List[str] = None
    execution_time: float = 0.0

@dataclass
class BrowserState:
    """Container for current browser state"""
    url: str
    title: str
    viewport_size: Dict[str, int]
    cookies: List[Dict[str, str]]
    ready_state: str
    network_idle: bool