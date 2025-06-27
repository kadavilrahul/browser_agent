#!/usr/bin/env python3
import asyncio
import time
from typing import List, Optional
from utils.logger import setup_logger
from utils.config import Config
from utils.models import AutomationStep, AutomationResult
from utils.js_helpers import JavaScriptHelpers

logger = setup_logger(__name__)
config = Config()
js = JavaScriptHelpers()

async def execute_automation_sequence(page, steps: List[AutomationStep]) -> AutomationResult:
    """
    Execute a sequence of automation steps
    Args:
        page: Pyppeteer page object
        steps: List of AutomationStep objects
    Returns:
        AutomationResult with execution details
    """
    start_time = time.time()
    screenshots = []
    completed_steps = 0
    
    try:
        if not config.automation_mode:
            raise Exception("Automation mode is disabled in config")

        logger.info("Starting automation sequence with %d steps", len(steps))
        
        for step in steps:
            try:
                # Execute step action
                if step.action == 'click':
                    await page.evaluate(js.click_element(step.selector))
                elif step.action == 'fill':
                    await page.evaluate(js.fill_form(step.selector, step.value))
                elif step.action == 'submit':
                    await page.evaluate(js.submit_form(step.selector))
                elif step.action == 'wait':
                    await asyncio.sleep(step.wait_time)
                elif step.action == 'scroll':
                    await page.evaluate(js.scroll_to_bottom())
                elif step.action == 'navigate':
                    await page.goto(step.value)
                else:
                    logger.warning("Unknown action: %s", step.action)
                    continue

                # Take screenshot if requested
                if step.screenshot:
                    screenshot_path = f"automation/step_{completed_steps+1}.png"
                    await page.screenshot({'path': screenshot_path})
                    screenshots.append(screenshot_path)

                completed_steps += 1
                await asyncio.sleep(step.wait_time)

            except Exception as e:
                logger.error("Step %d failed: %s", completed_steps+1, str(e))
                if step.screenshot:
                    screenshot_path = f"automation/error_step_{completed_steps+1}.png"
                    await page.screenshot({'path': screenshot_path})
                    screenshots.append(screenshot_path)
                break

        execution_time = time.time() - start_time
        logger.info("Automation completed %d/%d steps in %.2fs", completed_steps, len(steps), execution_time)
        
        return AutomationResult(
            steps_completed=completed_steps,
            success=completed_steps == len(steps),
            final_url=page.url,
            screenshots=screenshots,
            execution_time=execution_time
        )

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error("Automation sequence failed: %s", str(e))
        return AutomationResult(
            steps_completed=completed_steps,
            success=False,
            final_url=page.url,
            error=str(e),
            screenshots=screenshots,
            execution_time=execution_time
        )

async def generate_automation_steps(page, goal: str) -> List[AutomationStep]:
    """
    Generate automation steps based on natural language goal
    Args:
        page: Pyppeteer page object
        goal: Natural language description of automation goal
    Returns:
        List of AutomationStep objects
    """
    try:
        # TODO: Implement AI-based step generation
        logger.warning("AI step generation not yet implemented")
        return []
    except Exception as e:
        logger.error("Failed to generate automation steps: %s", str(e))
        return []