#!/usr/bin/env python3
"""
QuickNotify CLI Tool

Usage:
    python quicknotify_cli.py send --to <recipient> --subject <subject> --content <content>
    python quicknotify_cli.py template list
    python quicknotify_cli.py config test
    python quicknotify_cli.py records --status success --limit 10
"""

import argparse
import requests
import sys

class QuickNotifyCLI:
    def __init__(self, api_url='http://localhost:5000/api'):
        self.api_url = api_url
    
    def send_email(self, recipients, subject, content, cc=None):
        """Send email directly"""
        url = f'{self.api_url}/sender/send'
        data = {
            'recipients': recipients if isinstance(recipients, list) else [recipients],
            'subject': subject,
            'content': content,
            'cc': cc or []
        }
        
        try:
            response = requests.post(url, json=data)
            result = response.json()
            if result.get('success'):
                print(f"✅ {result['message']}")
                return True
            else:
                print(f"❌ {result.get('message', 'Failed to send email')}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_smtp(self):
        """Test SMTP configuration"""
        url = f'{self.api_url}/config/smtp/test'
        
        try:
            response = requests.post(url)
            result = response.json()
            if result.get('success'):
                print("✅ SMTP connection successful")
                return True
            else:
                print(f"❌ {result.get('message', 'SMTP test failed')}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def list_templates(self):
        """List all templates"""
        url = f'{self.api_url}/template/'
        
        try:
            response = requests.get(url)
            result = response.json()
            templates = result.get('templates', [])
            
            if not templates:
                print("No templates found")
                return
            
            print("\n📝 Available Templates:")
            print("-" * 60)
            for template in templates:
                print(f"ID: {template['id']} | Name: {template['name']}")
                print(f"   Subject: {template['subject']}")
                print()
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    def get_records(self, status='all', limit=10):
        """Get send records"""
        url = f'{self.api_url}/records/?status={status}&per_page={limit}'
        
        try:
            response = requests.get(url)
            result = response.json()
            records = result.get('records', [])
            
            if not records:
                print("No records found")
                return
            
            print("\n📋 Send Records:")
            print("-" * 80)
            for record in records:
                status_icon = "✅" if record['status'] == 'success' else "❌"
                print(f"{status_icon} {record['subject']}")
                print(f"   To: {', '.join(record['recipients'])}")
                print(f"   Status: {record['status']}")
                print()
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description='QuickNotify CLI - Email notification system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quicknotify_cli.py send --to user@example.com --subject "Test" --content "Hello"
  python quicknotify_cli.py template list
  python quicknotify_cli.py config test
  python quicknotify_cli.py records --status success --limit 10
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Send command
    send_parser = subparsers.add_parser('send', help='Send email')
    send_parser.add_argument('--to', required=True, help='Recipient email')
    send_parser.add_argument('--subject', required=True, help='Email subject')
    send_parser.add_argument('--content', required=True, help='Email content')
    send_parser.add_argument('--cc', help='CC recipients (comma separated)')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('action', choices=['test'], help='Config action')
    
    # Template command
    template_parser = subparsers.add_parser('template', help='Template management')
    template_parser.add_argument('action', choices=['list'], help='Template action')
    
    # Records command
    records_parser = subparsers.add_parser('records', help='Send records')
    records_parser.add_argument('--status', choices=['all', 'success', 'failed'], default='all', help='Filter by status')
    records_parser.add_argument('--limit', type=int, default=10, help='Number of records to show')
    
    args = parser.parse_args()
    
    cli = QuickNotifyCLI()
    
    if args.command == 'send':
        recipients = [r.strip() for r in args.to.split(',')]
        cc = [c.strip() for c in args.cc.split(',')] if args.cc else None
        cli.send_email(recipients, args.subject, args.content, cc=cc)
    
    elif args.command == 'config':
        if args.action == 'test':
            cli.test_smtp()
    
    elif args.command == 'template':
        if args.action == 'list':
            cli.list_templates()
    
    elif args.command == 'records':
        cli.get_records(status=args.status, limit=args.limit)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()