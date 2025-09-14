# clients/management/commands/send_follow_up_emails.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from clients.models import Client
from projects.models import Project

class Command(BaseCommand):
    help = 'Send automated follow-up emails'
    
    def handle(self, *args, **options):
        # Follow up on leads after 3 days
        three_days_ago = timezone.now() - timedelta(days=3)
        stale_leads = Client.objects.filter(
            status='lead',
            created_at__lt=three_days_ago,
            last_contact__isnull=True
        )
        
        for client in stale_leads:
            subject = f"Follow-up: LaTeX Services for {client.institution}"
            message = f"""
            Hi {client.first_name},
            
            I wanted to follow up on your inquiry about LaTeX services. 
            
            I'd love to help you with your project. Would you like to schedule 
            a quick 15-minute call to discuss your needs?
            
            Best regards,
            David Adams
            latex@dadams.cc
            """
            
            # In production, you'd actually send the email:
            # send_mail(subject, message, 'latex@dadams.cc', [client.email])
            
            self.stdout.write(f"Would send follow-up to {client.email}")
        
        # Follow up on quotes after 7 days
        week_ago = timezone.now() - timedelta(days=7)
        pending_quotes = Project.objects.filter(
            status='quoted',
            updated_at__lt=week_ago
        )
        
        for project in pending_quotes:
            subject = f"Quote follow-up: {project.title}"
            message = f"""
            Hi {project.client.first_name},
            
            I wanted to check if you had any questions about the quote 
            for "{project.title}".
            
            I'm happy to adjust the scope or timeline if needed.
            
            Best regards,
            David Adams
            """
            
            self.stdout.write(f"Would send quote follow-up to {project.client.email}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Processed {stale_leads.count()} lead follow-ups and '
                f'{pending_quotes.count()} quote follow-ups'
            )
        )
