"""
Decision Engine
Makes intelligent decisions about task execution
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.audit_logger_simple import AuditLogger
from src.odoo_client import OdooClient
from orchestrator.email_response_handler import EmailResponseHandler


class DecisionEngine:
    """
    Makes decisions about how to execute tasks
    """

    def __init__(self):
        """Initialize decision engine"""
        self.audit_logger = AuditLogger()

        # Initialize Odoo client
        try:
            self.odoo_client = OdooClient()
            self.odoo_client.authenticate()
        except Exception as e:
            self.audit_logger.log_event(
                event_type='odoo_init_error',
                details={'error': str(e)},
                severity='warning'
            )
            self.odoo_client = None

        # Initialize email response handler
        try:
            self.email_handler = EmailResponseHandler()
        except Exception as e:
            self.audit_logger.log_event(
                event_type='email_handler_init_error',
                details={'error': str(e)},
                severity='warning'
            )
            self.email_handler = None

    def analyze_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze task and determine execution plan

        Args:
            task: Task dictionary

        Returns:
            Execution plan
        """
        # Check specific task type first, then fall back to classified_type
        task_type = task.get('type', task.get('classified_type', 'general'))
        content = task.get('content', '')

        plan = {
            'task_type': task_type,
            'actions': [],
            'requires_approval': False,
            'estimated_risk': task.get('risk_level', 'medium')
        }

        # Route based on task type
        if task_type == 'email_inquiry':
            plan['actions'] = self._plan_email_inquiry_task(task)
        elif task_type == 'social_media_mention':
            plan['actions'] = self._plan_social_media_mention_task(task)
        elif task_type == 'email':
            plan['actions'] = self._plan_email_task(task)
        elif task_type == 'social_media':
            plan['actions'] = self._plan_social_media_task(task)
        elif task_type == 'odoo':
            plan['actions'] = self._plan_odoo_task(task)
        else:
            plan['actions'] = self._plan_general_task(task)

        return plan

    def _plan_email_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan email-related task"""
        content = task.get('content', '')

        # Extract email details (simplified - in production use NLP)
        actions = [{
            'type': 'mcp_tool',
            'tool': 'send_email',
            'params': {
                'to': task.get('recipient', 'unknown'),
                'subject': task.get('subject', 'Automated Message'),
                'body': content
            }
        }]

        return actions

    def _plan_email_inquiry_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan email inquiry task - create customer, lead, and send response"""
        actions = []

        # Step 1: Search for existing customer
        customer_email = task.get('customer_email') or task.get('sender_email')

        if customer_email:
            actions.append({
                'type': 'odoo',
                'action': 'search_customer',
                'params': {
                    'email': customer_email
                },
                'store_result_as': 'customer_id'
            })

            # Step 2: Create customer if not found
            actions.append({
                'type': 'odoo',
                'action': 'create_customer_if_needed',
                'params': {
                    'name': self._extract_name_from_email(task.get('email_from', '')),
                    'email': customer_email
                },
                'depends_on': 'customer_id'
            })

            # Step 3: Create lead
            actions.append({
                'type': 'odoo',
                'action': 'create_lead',
                'params': {
                    'name': f"Email Inquiry: {task.get('email_subject', 'Customer Inquiry')}",
                    'email': customer_email,
                    'description': task.get('email_body', '')[:500]  # Limit description
                }
            })

            # Step 4: Send auto-response
            if task.get('requires_response'):
                actions.append({
                    'type': 'email_response',
                    'params': {
                        'inquiry_data': task
                    }
                })

        return actions

    def _extract_name_from_email(self, from_header: str) -> str:
        """Extract name from email header"""
        if '<' in from_header:
            name = from_header.split('<')[0].strip().strip('"')
            if name:
                return name

        # Use email address
        email = from_header.split('<')[-1].strip('>')
        return email.split('@')[0].capitalize()

    def _plan_social_media_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan social media task"""
        content = task.get('content', '')
        platform = task.get('platform', 'facebook').lower()

        tool_map = {
            'facebook': 'post_facebook_page',
            'twitter': 'post_twitter',
            'instagram': 'post_instagram'
        }

        actions = [{
            'type': 'mcp_tool',
            'tool': tool_map.get(platform, 'post_facebook_page'),
            'params': {
                'message': content
            }
        }]

        return actions

    def _plan_social_media_mention_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan social media mention task - create lead for follow-up"""
        actions = []

        mention_type = task.get('mention_type', 'general_mention')
        platform = task.get('platform', 'unknown')
        from_user = task.get('from_user', 'Unknown User')
        message = task.get('message', '')

        # For customer inquiries and sales opportunities, create a lead
        if mention_type in ['customer_inquiry', 'sales_opportunity']:
            actions.append({
                'type': 'odoo',
                'action': 'create_lead',
                'params': {
                    'name': f"{platform.capitalize()} Inquiry from {from_user}",
                    'description': f"Platform: {platform}\nUser: {from_user}\nMessage: {message}",
                    'source_id': False  # Can be set to a specific source in Odoo
                }
            })

        # For positive engagement, just log it
        elif mention_type == 'positive_engagement':
            actions.append({
                'type': 'log',
                'message': f"Positive engagement on {platform} from {from_user}: {message[:100]}"
            })

        # For general mentions, log them
        else:
            actions.append({
                'type': 'log',
                'message': f"Social media mention on {platform} from {from_user}"
            })

        return actions

    def _plan_odoo_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan Odoo CRM task"""
        content = task.get('content', '').lower()
        actions = []

        # Detect intent
        if 'create customer' in content or 'new customer' in content:
            actions.append({
                'type': 'odoo',
                'action': 'create_customer',
                'params': {
                    'name': task.get('customer_name', 'Unknown Customer'),
                    'email': task.get('customer_email'),
                    'phone': task.get('customer_phone')
                }
            })

        if 'create lead' in content or 'new lead' in content:
            actions.append({
                'type': 'odoo',
                'action': 'create_lead',
                'params': {
                    'name': task.get('lead_title', 'New Opportunity'),
                    'email': task.get('customer_email'),
                    'description': task.get('description', content)
                }
            })

        if 'search customer' in content or 'find customer' in content:
            actions.append({
                'type': 'odoo',
                'action': 'search_customer',
                'params': {
                    'email': task.get('customer_email'),
                    'name': task.get('customer_name')
                }
            })

        return actions

    def _plan_general_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan general task"""
        return [{
            'type': 'log',
            'message': f"General task logged: {task.get('content', '')[:100]}"
        }]

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single action

        Args:
            action: Action dictionary

        Returns:
            Execution result
        """
        action_type = action.get('type')

        try:
            if action_type == 'odoo':
                return self._execute_odoo_action(action)
            elif action_type == 'mcp_tool':
                return self._execute_mcp_tool(action)
            elif action_type == 'email_response':
                return self._execute_email_response(action)
            elif action_type == 'log':
                return self._execute_log_action(action)
            else:
                return {
                    'success': False,
                    'error': f"Unknown action type: {action_type}"
                }

        except Exception as e:
            self.audit_logger.log_event(
                event_type='action_execution_error',
                details={'action': action, 'error': str(e)},
                severity='error'
            )
            return {
                'success': False,
                'error': str(e)
            }

    def _execute_odoo_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Odoo action"""
        if not self.odoo_client:
            return {
                'success': False,
                'error': 'Odoo client not available'
            }

        odoo_action = action.get('action')
        params = action.get('params', {})

        try:
            if odoo_action == 'create_customer':
                result_id = self.odoo_client.create_customer(**params)
                return {
                    'success': True,
                    'customer_id': result_id,
                    'message': f"Customer created with ID: {result_id}"
                }

            elif odoo_action == 'create_lead':
                result_id = self.odoo_client.create_lead(**params)
                return {
                    'success': True,
                    'lead_id': result_id,
                    'message': f"Lead created with ID: {result_id}"
                }

            elif odoo_action == 'search_customer':
                result_id = self.odoo_client.search_customer(**params)
                return {
                    'success': True,
                    'customer_id': result_id,
                    'found': result_id is not None
                }

            elif odoo_action == 'create_customer_if_needed':
                # Search first
                email = params.get('email')
                if email:
                    existing_id = self.odoo_client.search_customer(email=email)
                    if existing_id:
                        return {
                            'success': True,
                            'customer_id': existing_id,
                            'message': f"Customer already exists with ID: {existing_id}",
                            'created': False
                        }

                # Create if not found
                result_id = self.odoo_client.create_customer(**params)
                return {
                    'success': True,
                    'customer_id': result_id,
                    'message': f"Customer created with ID: {result_id}",
                    'created': True
                }

            else:
                return {
                    'success': False,
                    'error': f"Unknown Odoo action: {odoo_action}"
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _execute_mcp_tool(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool (placeholder - requires MCP client)"""
        tool = action.get('tool')
        params = action.get('params', {})

        # Log the intended action
        self.audit_logger.log_event(
            event_type='mcp_tool_call',
            details={'tool': tool, 'params': params},
            severity='info'
        )

        return {
            'success': True,
            'message': f"MCP tool '{tool}' would be called with params: {params}",
            'note': 'MCP client integration pending'
        }

    def _execute_email_response(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email response action"""
        if not self.email_handler:
            return {
                'success': False,
                'error': 'Email handler not available'
            }

        params = action.get('params', {})
        inquiry_data = params.get('inquiry_data', {})

        try:
            result = self.email_handler.handle_inquiry(inquiry_data)
            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _execute_log_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute log action"""
        message = action.get('message', 'No message')

        self.audit_logger.log_event(
            event_type='general_task',
            details={'message': message},
            severity='info'
        )

        return {
            'success': True,
            'message': 'Task logged successfully'
        }

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute complete execution plan

        Args:
            plan: Execution plan

        Returns:
            Execution results
        """
        actions = plan.get('actions', [])
        results = []

        for action in actions:
            result = self.execute_action(action)
            results.append({
                'action': action,
                'result': result
            })

            # Stop on first failure if critical
            if not result.get('success') and action.get('critical', False):
                break

        return {
            'success': all(r['result'].get('success', False) for r in results),
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
