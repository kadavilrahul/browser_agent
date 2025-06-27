#!/usr/bin/env python3
from typing import Dict, List, Optional

class JavaScriptHelpers:
    """Collection of reusable JavaScript snippets for browser automation"""

    @staticmethod
    def get_all_links() -> str:
        """JS to extract all links from page"""
        return """
            Array.from(document.querySelectorAll('a')).map(a => ({
                href: a.href,
                text: a.textContent.trim(),
                title: a.title
            }))
        """

    @staticmethod
    def get_all_images() -> str:
        """JS to extract all images from page"""
        return """
            Array.from(document.querySelectorAll('img')).map(img => ({
                src: img.src,
                alt: img.alt,
                width: img.naturalWidth,
                height: img.naturalHeight
            }))
        """

    @staticmethod
    def get_all_forms() -> str:
        """JS to extract all forms from page"""
        return """
            Array.from(document.querySelectorAll('form')).map(form => ({
                id: form.id,
                action: form.action,
                method: form.method,
                inputs: Array.from(form.elements).map(el => ({
                    name: el.name,
                    type: el.type,
                    value: el.value
                }))
            }))
        """

    @staticmethod
    def scroll_to_bottom() -> str:
        """JS to scroll page to bottom"""
        return "window.scrollTo(0, document.body.scrollHeight)"

    @staticmethod
    def wait_for_element(selector: str, timeout: int = 30000) -> str:
        """JS to wait for element to appear"""
        return f"""
            new Promise((resolve, reject) => {{
                const element = document.querySelector('{selector}');
                if (element) return resolve(element);
                
                const observer = new MutationObserver(() => {{
                    const element = document.querySelector('{selector}');
                    if (element) {{
                        observer.disconnect();
                        resolve(element);
                    }}
                }});
                
                observer.observe(document.body, {{
                    childList: true,
                    subtree: true
                }});
                
                setTimeout(() => {{
                    observer.disconnect();
                    reject(new Error('Timeout waiting for element'));
                }}, {timeout});
            }})
        """

    @staticmethod
    def click_element(selector: str) -> str:
        """JS to click element by selector"""
        return f"document.querySelector('{selector}').click()"

    @staticmethod
    def fill_form(selector: str, value: str) -> str:
        """JS to fill form field"""
        return f"document.querySelector('{selector}').value = '{value}'"

    @staticmethod
    def submit_form(selector: str) -> str:
        """JS to submit form"""
        return f"document.querySelector('{selector}').submit()"

    @staticmethod
    def get_page_metadata() -> str:
        """JS to extract page metadata"""
        return """
            ({
                title: document.title,
                description: document.querySelector('meta[name="description"]')?.content,
                keywords: document.querySelector('meta[name="keywords"]')?.content,
                viewport: document.querySelector('meta[name="viewport"]')?.content,
                canonical: document.querySelector('link[rel="canonical"]')?.href
            })
        """