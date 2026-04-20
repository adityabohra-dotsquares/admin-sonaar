from django.core.management.base import BaseCommand
from adminuser.models.admin import CustomAdminUser  # Import your custom admin model
from django.utils.crypto import get_random_string


class Command(BaseCommand):
    help = "Creates a new CustomAdminUser"

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, help="Email for the new admin user")
        parser.add_argument(
            "--username", type=str, help="Username for the new admin user"
        )
        parser.add_argument(
            "--password", type=str, help="Password for the new admin user"
        )

    def handle(self, *args, **options):
        email = options.get("email")
        username = options.get("username")
        password = options.get("password") or get_random_string(8)

        if not email or not username:
            self.stdout.write(self.style.ERROR("Email and Username are required!"))
            return

        if CustomAdminUser.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR("A user with this email already exists!")
            )
            return

        admin_user = CustomAdminUser.objects.create_super_admin(
            email=email, username=username, password=password
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'CustomAdminUser "{username}" created successfully with password: {password}'
            )
        )
