import os
import re
from django import forms
from django.conf import settings
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives, send_mail
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, URLValidator
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.forms.widgets import ClearableFileInput

from .models.email import EmailTemplate, EmailReceiver, EmailTriggers
from adminuser.models.vendor import Vendor, Country
from adminuser.models.admin import CustomAdminUser, AdminRoles, AdminPermission, ACTIONS
from adminuser.models.social_media import SocialMediaLink
from adminuser.models.currency import Currency

from .constants import *
from adminuser.constants import POST_CODES

from site_settings.models import Menu, MenuItem

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB in bytes

ROLE_CHOICES = (
    (SUPERADMIN, "Super Admin"),
    (ORDERMANAGER, "Order Manager"),
    (CATALOGSUPERVISOR, "Catalog Supervisor"),
    (SUPPORTAGENT, "Support Agent"),
    (MARKETINGEXECUTIVE, "Marketing Executive"),
    (SHIPPINGCOORDINATOR, "Shipping Coordinator"),
)


# Define zone code choices
ZONE_CODE_CHOICES = [
    ('ACT', 'ACT'),
    ('NSW_M', 'NSW_M'),
    ('NSW_R', 'NSW_R'),
    ('NT_M', 'NT_M'),
    ('QLD_M', 'QLD_M'),
    ('QLD_R', 'QLD_R'),
    ('REMOTE', 'REMOTE'),
    ('SA_M', 'SA_M'),
    ('SA_R', 'SA_R'),
    ('TAS_M', 'TAS_M'),
    ('TAS_R', 'TAS_R'),
    ('VIC_M', 'VIC_M'),
    ('VIC_R', 'VIC_R'),
    ('WA_M', 'WA_M'),
    ('WA_R', 'WA_R'),
]


POST_CODE_CHOICES=[
    (post_code, post_code) for post_code in POST_CODES
]

# Define zone name choices
ZONE_NAME_CHOICES = [
    ('Adelaide', 'Adelaide'),
    ('Australian Antarctic Territory', 'Australian Antarctic Territory'),
    ('Ballarat', 'Ballarat'),
    ('Brisbane', 'Brisbane'),
    ('Canberra', 'Canberra'),
    ('Christmas Island', 'Christmas Island'),
    ('Cocos Islands', 'Cocos Islands'),
    ('Coolangatta', 'Coolangatta'),
    ('Geelong', 'Geelong'),
    ('Gold Coast', 'Gold Coast'),
    ('Gosford', 'Gosford'),
    ('Ipswich', 'Ipswich'),
    ('Melbourne', 'Melbourne'),
    ('Newcastle', 'Newcastle'),
    ('Norfolk Island', 'Norfolk Island'),
    ('NSW Country North', 'NSW Country North'),
    ('NSW Country South', 'NSW Country South'),
    ('NT Far Country', 'NT Far Country'),
    ('NT Near Country', 'NT Near Country'),
    ('Perth', 'Perth'),
    ('QLD Far Country', 'QLD Far Country'),
    ('QLD Mid Country', 'QLD Mid Country'),
    ('QLD Near Country', 'QLD Near Country'),
    ('SA Country', 'SA Country'),
    ('Sunshine Coast', 'Sunshine Coast'),
    ('Sydney', 'Sydney'),
    ('Tasmania Country', 'Tasmania Country'),
    ('Tasmania Metro', 'Tasmania Metro'),
    ('Tweed Heads', 'Tweed Heads'),
    ('VIC Far Country', 'VIC Far Country'),
    ('VIC Near Country', 'VIC Near Country'),
    ('WA Far Country', 'WA Far Country'),
    ('WA Near Country', 'WA Near Country'),
    ('Wollongong', 'Wollongong'),
]

# Example choices for categories; replace with your actual categories
CATEGORY_CHOICES = [
    ("cat1", "Category 1"),
    ("cat2", "Category 2"),
    ("cat3", "Category 3"),
]




class CustomAdminLoginForm(forms.Form):
    # email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Email"}))
    # password = forms.CharField(
    #     widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    # )
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            try:
                user = CustomAdminUser.objects.get(email=email)
            except CustomAdminUser.DoesNotExist:
                raise forms.ValidationError("Invalid email or password")

            if not user.check_password(password):
                user.failed_login_attempts += 1
                user.last_failed_login = timezone.now()
                if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                    user.is_blocked = True
                    user.blocked_until = timezone.now() + settings.BLOCK_DURATION
                    # Send email notification
                    send_mail(
                        subject="Account Blocked",
                        message=f"Your account has been blocked due to {settings.MAX_FAILED_LOGIN_ATTEMPTS} failed login attempts. "
                        f"You can try logging in again after {settings.BLOCK_DURATION}.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                    )

                user.save()
                raise forms.ValidationError("Invalid email or password")

            if not user.is_active:
                raise forms.ValidationError("This account is inactive")

            cleaned_data["user"] = user

        return cleaned_data


class CustomAdminUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    class Meta:
        model = CustomAdminUser
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "extra_permissions",
            "password",
            "is_active",
        ]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
            "extra_permissions": forms.CheckboxSelectMultiple(),
            "is_active": forms.CheckboxInput(),
        }

    def __init__(self, role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("ROLE", role)
        # Exclude role with ID = 1
        self.fields["role"].queryset = AdminRoles.objects.exclude(id=1)
        if role == SUPERADMIN:
            self.fields["role"].queryset = AdminRoles.objects.exclude(id=1)
        if role == ADMIN:
            self.fields["role"].queryset = AdminRoles.objects.exclude(id=1).exclude(
                role=ADMIN
            )


class CustomAdminUserUpdateForm(forms.ModelForm):
    # password = forms.CharField(widget=forms.PasswordInput, label="Password")
    class Meta:
        model = CustomAdminUser
        fields = [
            "first_name",
            "last_name",
            "role",
            "extra_permissions",
            "is_active",
        ]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
            "extra_permissions": forms.CheckboxSelectMultiple(),
            "is_active": forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude role with ID = 1
        self.fields["role"].queryset = AdminRoles.objects.exclude(id=1)


class AdminRolesForm(forms.ModelForm):
    class Meta:
        model = AdminRoles
        fields = [
            "role",
            "permissions",
        ]
        widgets = {
            "permissions": forms.CheckboxSelectMultiple(),  # Makes it easier to select multiple permissions
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally, you can filter permissions dynamically if needed
        self.fields["permissions"].queryset = AdminPermission.objects.all()
        # self.fields["updated_by"].required = False  # allow null

    def clean_role(self):
        role = self.cleaned_data.get("role")
        if role not in dict(ROLE_CHOICES).keys():
            raise forms.ValidationError(
                f"Invalid role '{role}'. Must be one of {list(dict(ROLE_CHOICES).keys())}."
            )
        return role



from adminuser.constants import MODULES

# Extract (value, label) for ChoiceField
MODULE_CHOICES = [(m[0], m[1]) for m in MODULES]


class AdminPermissionForm(forms.ModelForm):
    module = forms.ChoiceField(
        choices=MODULE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select", "onchange": "updateActions()"}),
    )
    action = forms.MultipleChoiceField(
        choices=ACTIONS,
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = AdminPermission
        fields = ["module"]

    def clean(self):
        cleaned_data = super().clean()
        module = cleaned_data.get("module")
        actions = cleaned_data.get("action")

        if module and actions:
            # Find allowed actions for this module from MODULES constant
            allowed_actions = []
            for m_item in MODULES:
                if m_item[0] == module:
                    allowed_actions = m_item[2]
                    break

            invalid_actions = [a for a in actions if a not in allowed_actions]
            if invalid_actions:
                raise forms.ValidationError(
                    f"Actions {invalid_actions} are not allowed for module '{module}'."
                )

            # Set a valid action on the instance for model validation
            if self.instance:
                self.instance.action = actions[0]

        return cleaned_data


# class AdminPasswordResetForm(forms.Form):
#     email = forms.EmailField(label="Admin Email", widget=forms.EmailInput(attrs={"class": "form-control"}))

#     def clean_email(self):
#         email = self.cleaned_data["email"]
#         if not CustomAdminUser.objects.filter(email=email).exists():
#             raise forms.ValidationError("No admin found with this email address.")
#         return email

#     def save(self, request, use_https=False, token_generator=default_token_generator,
#              email_template_name="adminuser/password_reset_email.html",
#              subject_template_name="adminuser/password_reset_subject.txt",
#              from_email=None):
#         email = self.cleaned_data["email"]
#         for user in CustomAdminUser.objects.filter(email=email, is_active=True):
#             context = {
#                 "email": user.email,
#                 "domain": request.get_host(),
#                 "site_name": "Admin Panel",
#                 "uid": urlsafe_base64_encode(force_bytes(user.pk)),
#                 "user": user,
#                 "token": token_generator.make_token(user),
#                 "protocol": "https" if use_https else "http",
#             }
#             subject = render_to_string(subject_template_name, context).strip()
#             message = render_to_string(email_template_name, context)
#             send_mail(subject, message, from_email, [user.email])
# class AdminPasswordResetForm(forms.Form):
#     email = forms.EmailField(label="Email", max_length=254)

#     def get_users(self, email):
#         from .models import CustomAdminUser
#         return CustomAdminUser.objects.filter(email__iexact=email, is_active=True)

#     def save(
#         self,
#         domain_override=None,
#         subject_template_name="admin_users/password_reset_subject.txt",
#         email_template_name="admin_users/password_reset_email.html",
#         use_https=False,
#         token_generator=default_token_generator,
#         from_email=None,
#         request=None,
#         html_email_template_name=None,  # accept this param
#         extra_email_context=None,
#     ):
#         """
#         Sends password reset emails to users.
#         """
#         from django.core.mail import EmailMultiAlternatives
#         from django.template.loader import render_to_string
#         from django.utils.http import urlsafe_base64_encode
#         from django.utils.encoding import force_bytes
#         from django.contrib.auth.tokens import default_token_generator
#         from django.conf import settings

#         for user in self.get_users(self.cleaned_data["email"]):
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             token = token_generator.make_token(user)
#             context = {
#                 "email": user.email,
#                 "domain": domain_override or request.get_host(),
#                 "site_name": "Admin Portal",
#                 "uid": uid,
#                 "user": user,
#                 "token": token,
#                 "protocol": "https" if use_https else "http",
#                 **(extra_email_context or {}),
#             }

#             subject = render_to_string(subject_template_name, context)
#             subject = "".join(subject.splitlines())

#             body = render_to_string(email_template_name, context)

#             email_message = EmailMultiAlternatives(subject, body, from_email, [user.email])

#             if html_email_template_name:
#                 html_email = render_to_string(html_email_template_name, context)
#                 email_message.attach_alternative(html_email, "text/html")

#             email_message.send()


class AdminPasswordResetForm(forms.Form):
    email = forms.EmailField(
        label="Admin Email",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
        max_length=254,
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not CustomAdminUser.objects.filter(
            email__iexact=email, is_active=True
        ).exists():
            raise forms.ValidationError(
                "No active admin found with this email address."
            )
        return email

    def get_users(self, email):
        """
        Return a queryset of all active admin users matching the given email.
        """
        return CustomAdminUser.objects.filter(email__iexact=email, is_active=True)

    def save(
        self,
        domain_override=None,
        subject_template_name="adminuser/password_reset_subject.txt",
        email_template_name="adminuser/password_reset_email.txt",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Sends a password reset email to admin users.
        """
        for user in self.get_users(self.cleaned_data["email"]):
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)

            context = {
                "email": user.email,
                "domain": domain_override or request.get_host(),
                "site_name": "Admin Panel",
                "uid": uid,
                "user": user,
                "token": token,
                "protocol": "https" if use_https else "http",
            }

            if extra_email_context:
                context.update(extra_email_context)

            subject = render_to_string(subject_template_name, context)
            subject = "".join(subject.splitlines())  # avoid newlines in subject
            body = render_to_string(email_template_name, context)

            # ✅ If HTML email is provided, use EmailMultiAlternatives
            if html_email_template_name:
                email_message = EmailMultiAlternatives(
                    subject, body, from_email, [user.email]
                )
                html_email = render_to_string(html_email_template_name, context)
                email_message.attach_alternative(html_email, "text/html")
                email_message.send()
            else:
                send_mail(subject, body, from_email, [user.email])


class VendorCreateForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            "managed_by",
            "name",
            "country",
            "tax_id_label",
            "tax_id",
            "email",
            "phone",
            "address_line1",
            "address_line2",
            "city",
            "state_province",
            "postal_code",
            "latitude",
            "longitude",
            "currency",
            "credit_limit",
            "website",
            "notes",
        ]

    # def __init__(self):
    #     self.fields['managed_by'].queryset = CustomAdminUser.objects.filter(role__ne=1)


class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True


class ProductForm(forms.Form):
    fast_dispatch = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    free_shipping = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    hs_code = forms.CharField(
        label="HS Code",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    sku = forms.CharField(
        label="SKU",
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "required": "required"}),
    )
    has_variants = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Has Variants",
    )
    title = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "required": "required"}),
    )
    warranty = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 4, "class": "form-control", "required": "required"}
        )
    )
    bundle_group_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    # videos = forms.CharField(
    #     widget=forms.TextInput(),
    #     required=False,
    # )
    videos = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "pattern": r"^(?:\s*(https?:\/\/[^\s,]+)\s*(?:,\s*(https?:\/\/[^\s,]+)\s*)*)?$",
            "title": "Enter valid URLs separated by commas (http:// or https:// required, spaces around commas allowed)",
            "placeholder": "http://example.com/video.mp4, https://example.com/another.mp4"
        }),
        required=False,
    )
    def clean_videos(self):
        value = self.cleaned_data.get('videos')
        
        # If field is empty or just whitespace, it's allowed (required=False)
        if not value or not value.strip():
            return value

        url_validator = URLValidator()
        urls = [url.strip() for url in value.split(',') if url.strip()]

        if not urls:
            return value  # Only commas or spaces — still valid empty case

        for url in urls:
            try:
                url_validator(url)
            except ValidationError:
                raise ValidationError(f'"{url}" is not a valid URL.')

        # Optionally normalize the output (remove extra spaces, consistent commas)
        return ', '.join(urls)
        
        # return value  # Return original input to preserve user's formatting

    price = forms.DecimalField(
        min_value=0.00,
        required=False,
        max_digits=10,
        decimal_places=2,
       widget=forms.TextInput(
        attrs={
            "inputmode": "decimal",
            "pattern": r"^\d{1,8}(\.\d{1,2})?$",  # Allows up to 8 digits before decimal, 2 after (adjust as needed for max_digits=10)
            "title": "Enter a valid price (e.g., 123.45), up to 2 decimal places",
            "class": "form-control price",
            "placeholder": "0.00",  # Optional: Guides user input
            "onkeypress": "return event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46"  # JS to allow only 0-9 and '.' (decimal point)
        }
    ),
    )
    cost_price = forms.DecimalField(
        min_value=0.00,
        required=False,
        max_digits=10,
        decimal_places=2,
       widget=forms.TextInput(
        attrs={
            "inputmode": "decimal",
            "pattern": r"^\d{1,8}(\.\d{1,2})?$",  # Allows up to 8 digits before decimal, 2 after (adjust as needed for max_digits=10)
            "title": "Enter a valid price (e.g., 123.45), up to 2 decimal places",
            "class": "form-control cost_price",
            "placeholder": "0.00",  # Optional: Guides user input
            "onkeypress": "return event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46"  # JS to allow only 0-9 and '.' (decimal point)
        }
    ),
    )
    rrp_price = forms.DecimalField(
        label="Compare-at price",
        min_value=0.00,
        required=False,
        max_digits=10,
        decimal_places=2,
              widget=forms.TextInput(
        attrs={
            "inputmode": "decimal",
            "pattern": r"^\d{1,8}(\.\d{1,2})?$",  # Allows up to 8 digits before decimal, 2 after (adjust as needed for max_digits=10)
            "title": "Enter a valid price (e.g., 123.45), up to 2 decimal places",
            "class": "form-control rrp_price",
            "placeholder": "0.00",  # Optional: Guides user input
            "onkeypress": "return event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46"  # JS to allow only 0-9 and '.' (decimal point)
        }
    ),
    )
    status = forms.ChoiceField(
        choices=[
            ("active", "Active"),
            ("archived", "Archived"),
            ("draft", "Draft"),
            ("discontinued", "Discontinued"),
        ]
    )
    product_condition = forms.ChoiceField(
        choices=[
            ("New", "New"),
            ("Refurbished", "Refurbished"),
            ("New(Open box)", "New(Open box)"),
        ]
    )

    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control","hidden": "hidden",
            }
        ),
    )
    weight = forms.DecimalField(
        label="Weight",
        min_value=0,
        required=False,
        max_digits=10,
        decimal_places=2,
              widget=forms.TextInput(
        attrs={
            "inputmode": "decimal",
            "pattern": r"^\d{1,8}(\.\d{1,2})?$",  # Allows up to 8 digits before decimal, 2 after (adjust as needed for max_digits=10)
            "title": "Enter a valid price (e.g., 123.45), up to 2 decimal places",
            "class": "form-control rrp_price",
            "placeholder": "0.00",  # Optional: Guides user input
            "onkeypress": "return event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46"  # JS to allow only 0-9 and '.' (decimal point)
        }
    ),
    )


    
    supplier = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    ean = forms.CharField(label="EAN", max_length=50, required=False)
    category_id = forms.CharField(
        required=True,
        widget=forms.Select(attrs={"class": "form-select select2Category"}),
    )
    brand_id = forms.CharField(
        widget=forms.Select(attrs={"class": "form-select select2Brand"})
    )
    stock = forms.IntegerField(
        min_value=0,
        label="Inventory",
        required=False,
        widget=forms.NumberInput(
            attrs={
                "inputmode": "numeric",
                "class": "form-control stock",
                "oninput": "this.value = this.value.replace(/[^0-9]/g, '');",
            }
        ),
    )

    key_features = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}), required=False
    )
    images = forms.FileField(
        widget=MultipleFileInput(attrs={"multiple": True,
         "accept": "image/jpeg,image/png,.jpg,.jpeg,.png"
         }),
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],  # Server-side restriction
    )


    precautionary_note = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}), required=False
    )
    care_instructions = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}), required=False
    )
    warranty = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)
    SHIPS_FROM_CHOICES = [
    ('SBAU', 'SBAU'),
    ('USA', 'USA'),
    ('China', 'China'),
    ('Local 3PL', 'Local 3PL'),
]

    ships_from_location = forms.ChoiceField(
    choices=SHIPS_FROM_CHOICES,
    required=True,
    widget=forms.Select(attrs={"class": "form-control"}),
)
    handling_time_days = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "step": "1",
                "inputmode": "integer",
                "class": "form-control",
                "required": "required",
                "oninput": "this.value = this.value.replace(/[^0-9.]/g, '').replace(/(\\..*)\\./g, '$1');",
            }
        ),
    )
    length = forms.DecimalField(
        label="Length(cm)",
        min_value=0,
        required=False,
        max_digits=10,
        decimal_places=2,
              widget=forms.TextInput(
        attrs={
            "inputmode": "decimal",
            "pattern": r"^\d{1,8}(\.\d{1,2})?$",  # Allows up to 8 digits before decimal, 2 after (adjust as needed for max_digits=10)
            "title": "Enter a valid price (e.g., 123.45), up to 2 decimal places",
            "class": "form-control rrp_price",
            "placeholder": "0.00",  # Optional: Guides user input
            "onkeypress": "return event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46"  # JS to allow only 0-9 and '.' (decimal point)
        }
    ),
    )
    width = forms.DecimalField(
        label="Width(cm)",
        min_value=0,
        required=False,
        max_digits=10,
        decimal_places=2,
              widget=forms.TextInput(
        attrs={
            "inputmode": "decimal",
            "pattern": r"^\d{1,8}(\.\d{1,2})?$",  # Allows up to 8 digits before decimal, 2 after (adjust as needed for max_digits=10)
            "title": "Enter a valid price (e.g., 123.45), up to 2 decimal places",
            "class": "form-control rrp_price",
            "placeholder": "0.00",  # Optional: Guides user input
            "onkeypress": "return event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46"  # JS to allow only 0-9 and '.' (decimal point)
        }
    ),
    )

    height = forms.DecimalField(
        label="Height(cm)",
        min_value=0,
        required=False,
        max_digits=10,
        decimal_places=2,
              widget=forms.TextInput(
        attrs={
            "inputmode": "decimal",
            "pattern": r"^\d{1,8}(\.\d{1,2})?$",  # Allows up to 8 digits before decimal, 2 after (adjust as needed for max_digits=10)
            "title": "Enter a valid price (e.g., 123.45), up to 2 decimal places",
            "class": "form-control rrp_price",
            "placeholder": "0.00",  # Optional: Guides user input
            "onkeypress": "return event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46"  # JS to allow only 0-9 and '.' (decimal point)
        }
    ),
    )
    page_title = forms.CharField(
        label="Page Title",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    meta_description = forms.CharField(
        label="Meta Description",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    meta_keywords = forms.CharField(
        label="Meta Keywords",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    
    url_handle = forms.CharField(
        label="URL Handle",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    canonical_url = forms.CharField(
        label="Canonical URL",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    def clean_price(self):
        price = self.cleaned_data.get("price")
        has_variants = self.cleaned_data.get("has_variants")
        if not has_variants and price is None:
            raise ValidationError("Price is required")
        return price
    def clean_cost_price(self):
        cost_price = self.cleaned_data.get("cost_price")
        has_variants = self.cleaned_data.get("has_variants")
        if not has_variants and cost_price is None:
            raise ValidationError("Cost price is required")
        return cost_price
    def clean_rrp_price(self):
        rrp_price = self.cleaned_data.get("rrp_price")
        has_variants = self.cleaned_data.get("has_variants")
        if not has_variants and rrp_price is None:
            raise ValidationError("RRP price is required")
        return rrp_price
    def clean_stock(self):
        stock = self.cleaned_data.get("stock")
        has_variants = self.cleaned_data.get("has_variants")
        if not has_variants and stock is None:
            raise ValidationError("Stock is required")
        return stock


class BrandCreateForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=True,
        label="Brand Name",
        widget=forms.TextInput(attrs={"placeholder": "Enter brand name"}),
    )

    logo_image = forms.FileField(
        required=False,
        label="Logo Image",
        widget=forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,.jpg,.jpeg,.png"}),
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
    )

    banner_image = forms.FileField(
        required=False,
        label="Banner Image",
        widget=forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,.jpg,.jpeg,.png"}),
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
    )


class CategoryForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        label="Category Name",
        widget=forms.TextInput(
            attrs={"placeholder": "Enter category name", "class": "form-control"}
        ),
    )
    category_code = forms.CharField(
        max_length=100,
        required=True,
        label="Category Code",
        widget=forms.TextInput(
            attrs={"placeholder": "Enter category code", "class": "form-control"}
        ),
    )
    parent_id = forms.CharField(required=False, widget=forms.Select(attrs={"class": "select2"}))
    image = forms.ImageField(  # Logo image
        label="Category Image (Logo)",
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "image/jpeg,image/jpg,image/png", }),
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
    )


    icon = forms.ImageField(  # Icon
        label="Icon",
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "image/jpeg,image/jpg,image/png", }),
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
    )
    # status = forms.BooleanField(
    #     required=False,
    #     label="Is Active",
    #     widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    # )







    # Dynamically populate parent_id choices
    def __init__(self, *args, **kwargs):
        # parent_choices = kwargs.pop("parent_choices", [])
        super().__init__(*args, **kwargs)
        # self.fields["parent_id"].choices = [("", "None")] + parent_choices


# class EmailTemplateForm(forms.ModelForm):
#     class Meta:
#         model = EmailTemplates
#         fields = [
#             "name",
#             "subject",
#             "template",
#             "created_by",
#             "updated_by",
#             "is_active",
#         ]


class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = [
            "name",
            "symbol",
            # "template",
            # "created_by",
            # "updated_by",
            # "is_active",
        ]


def validate_file_extension(value):
    if not value.name.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
        raise ValidationError(
            "Unsupported file format. Only CSV, XLS, and XLSX files are allowed."
        )


def validate_file_size(value):
    if value.size > MAX_UPLOAD_SIZE:
        raise ValidationError(
            f"File too large. Maximum allowed size is 10 MB. Your file is {value.size // (1024*1024)} MB."
        )


class ProductImportForm(forms.Form):
    import_file = forms.FileField(
        label="Import Products (CSV, XLSX, XLS)",
        help_text="Maximum file size: 10 MB. Supported formats: .csv, .xlsx, .xls",
        validators=[validate_file_extension, validate_file_size],
        widget=forms.FileInput(
            attrs={
                "accept": ".csv,.xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv"
            }
        ),
    )
    def clean_import_file(self):
        file = self.cleaned_data["import_file"]

        # Double-check size and extension (security)
        if file.size > MAX_UPLOAD_SIZE:
            raise ValidationError("File exceeds 10 MB limit.")

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError("Invalid file type.")

        return file


class ZoneRatesImportForm(forms.Form):
    import_file = forms.FileField(
        label="Import Zone Rates (CSV, XLSX, XLS)",
        help_text="Maximum file size: 10 MB. Supported formats: .csv, .xlsx, .xls",
        validators=[validate_file_extension, validate_file_size],
        widget=forms.FileInput(
            attrs={
                "accept": ".csv,.xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv"
            }
        ),
    )
    def clean_import_file(self):
        file = self.cleaned_data["import_file"]

        # Double-check size and extension (security)
        if file.size > MAX_UPLOAD_SIZE:
            raise ValidationError("File exceeds 10 MB limit.")

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError("Invalid file type.")

        return file


class PriceQuantityImportForm(forms.Form):
    import_file = forms.FileField(
        label="Import Price Quantity (CSV, XLSX, XLS)",
        help_text="Maximum file size: 10 MB. Supported formats: .csv, .xlsx, .xls",
        validators=[validate_file_extension, validate_file_size],
        widget=forms.FileInput(
            attrs={
                "accept": ".csv,.xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv"
            }
        ),
    )
    def clean_import_file(self):
        file = self.cleaned_data["import_file"]

        # Double-check size and extension (security)
        if file.size > MAX_UPLOAD_SIZE:
            raise ValidationError("File exceeds 10 MB limit.")

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError("Invalid file type.")

        return file


class BrandImportForm(forms.Form):
    import_file = forms.FileField(
        label="Import Brands (CSV, XLSX, XLS)",
        help_text="Maximum file size: 10 MB. Supported formats: .csv, .xlsx, .xls",
        validators=[validate_file_extension, validate_file_size],
        widget=forms.FileInput(
            attrs={
                "accept": ".csv,.xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv",
                "class": "form-control"
            }
        ),
    )

    def clean_import_file(self):
        file = self.cleaned_data["import_file"]
        if file.size > MAX_UPLOAD_SIZE:
            raise ValidationError(
                f"File too large. Maximum allowed size is 10 MB. Your file is {file.size // (1024*1024)} MB."
            )
        return file


class ZonesImportForm(forms.Form):
    import_file = forms.FileField(
        label="Import Zone (CSV, XLSX, XLS)",
        help_text="Maximum file size: 10 MB. Supported formats: .csv, .xlsx, .xls",
        validators=[validate_file_extension, validate_file_size],
        widget=forms.FileInput(
            attrs={
                "accept": ".csv,.xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv"
            }
        ),
    )

    def clean_import_file(self):
        file = self.cleaned_data["import_file"]

        # Double-check size and extension (security)
        if file.size > MAX_UPLOAD_SIZE:
            raise ValidationError("File exceeds 10 MB limit.")

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError("Invalid file type.")

        return file


class PostcodeImportForm(forms.Form):
    import_file = forms.FileField(
        label="Import Postcode (CSV, XLSX, XLS)",
        help_text="Maximum file size: 10 MB. Supported formats: .csv, .xlsx, .xls",
        validators=[validate_file_extension, validate_file_size],
        widget=forms.FileInput(
            attrs={
                "accept": ".csv,.xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv"
            }
        ),
    )

    def clean_import_file(self):
        file = self.cleaned_data["import_file"]

        # Double-check size and extension (security)
        if file.size > MAX_UPLOAD_SIZE:
            raise ValidationError("File exceeds 10 MB limit.")

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError("Invalid file type.")

        return file


class RateByZoneForm(forms.Form):
    """
    Django form for creating/editing RateByZone records.
    Includes only the requested fields: zone, rate, and product_id.
    """

    zone = forms.CharField(
        max_length=255,
        required=True,
        label="Zone",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter zone name"}
        ),
    )

    rate = forms.FloatField(
        required=True,
        initial=0.0,
        min_value=0.0,  # Optional: prevent negative rates
        label="Rate",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",  # Allows decimal input
                "placeholder": "0.00",
                "inputmode": "decimal",
                "oninput": "this.value = this.value.replace(/[^0-9.]/g, '').replace(/(\\..*)\\./g, '$1');",
            }
        ),
    )

    product_id = forms.CharField(
        max_length=36,
        required=True,
        label="Product ID",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Product"}
        ),
    )


class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['key', 'subject', 'body_text', 'body_html']
        widgets = {
            'body_text': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
            'body_html': forms.Textarea(attrs={'rows': 100, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make key read-only on update (not on create)
        if self.instance and self.instance.pk:
            self.fields['key'].disabled = True


class EmailReceiverForm(forms.ModelForm):
    class Meta:
        model = EmailReceiver
        fields = ['template', 'roles', 'users', 'emails']
        widgets = {
            'template': forms.Select(attrs={'class': 'form-select'}),
            'roles': forms.CheckboxSelectMultiple(),
            'users': forms.CheckboxSelectMultiple(),
            'emails': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Comma-separated emails'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally filter users or roles if needed
        self.fields['template'].empty_label = "Select Template"


class EmailTriggerForm(forms.ModelForm):
    class Meta:
        model = EmailTriggers
        fields = ['trigger', 'data']
        widgets = {
            'trigger': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.Textarea(attrs={
                'rows': 8,
                'class': 'form-control',
                'placeholder': '[{"type": "role", "value": "admin", "template_id": "1"}, ...]',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['trigger'].disabled = True

class DeliveryZoneForm(forms.Form):
    zone_code = forms.CharField(
        max_length=50,
        widget=forms.Select(attrs={'class': 'form-select', "required": "required"}, choices=ZONE_CODE_CHOICES),
        help_text="Select from existing zone codes or type a new one"
    )
    zone_name = forms.CharField(
        max_length=100,
        widget=forms.Select(attrs={'class': 'form-select', "required": "required"}, choices=ZONE_NAME_CHOICES),
        help_text="Select from existing zone names or type a new one"
    )
    is_active = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    uuid = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, is_edit=False, **kwargs):
        super().__init__(*args, **kwargs)
        if is_edit:
            # For edit: make zone_code readonly
            self.fields['zone_code'].widget.attrs['readonly'] = 'readonly'
            self.fields['zone_code'].help_text = "Zone code cannot be changed after creation"
        else:
            # For create: allow editing zone_code
            self.fields['zone_code'].help_text = "Select from existing zone codes or type a new one"


class PostcodeZoneForm(forms.Form):
    postcode = forms.CharField(
        max_length=10,
        widget=forms.Select(attrs={'class': 'form-select', "required": "required"}, choices=POST_CODE_CHOICES),
        help_text="e.g., 2000, 3000-3005"
    )
    zone_code = forms.ChoiceField(
        choices=[],  # Initially empty
        widget=forms.Select(attrs={'class': 'form-select', "required": "required"})
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # If you're editing, you might want to hide/show UUID
    uuid = forms.UUIDField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, is_edit=False, **kwargs):
        zone_choices = kwargs.pop('zone_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['zone_code'].choices = zone_choices
        # if is_edit:
            # self.fields['postcode'].widget.attrs['readonly'] = True  # Often postcode can't change
            # self.fields['postcode'].help_text = "Postcode cannot be changed after creation"


def validate_rate(value):
    """
    Validates that the rate is either:
    - "NS"
    - A single positive number (integer or float, e.g., "2000" or "2000.5")
    - A range of positive numbers separated by a hyphen (e.g., "3000-3005" or "3000.0-3005.5"), where start <= end
    """
    if value == "NS":
        return value
    
    # Regex to match positive number (integer or float)
    number_pattern = r'^\d+(\.\d+)?$'
    
    # Check for single positive number
    if re.match(number_pattern, value):
        num = float(value)
        if num >= 0:
            return value
        else:
            raise ValidationError("Must be a positive number (greater than 0).")
    
    raise ValidationError("Invalid input. Must be 'NS', a positive number (e.g., 2000 or 2000.5), or a range (e.g., 3000-3005 or 3000.0-3005.5).")


class ShippingRateByZoneForm(forms.Form):
    product_identifier = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control',"required": "required"}),
        help_text="e.g., 2000, 3000-3005"
    )
    zone_code =  forms.ChoiceField(
        choices=[],  # Initially empty
        widget=forms.Select(attrs={'class': 'form-select', "required": "required"})
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    rate = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control','required': 'required'}),
        help_text="e.g., 2000, 3000-3005",
        validators=[validate_rate]
    )
    # If you're editing, you might want to hide/show UUID
    uuid = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, is_edit=False, **kwargs):
        zone_choices = kwargs.pop('zone_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['zone_code'].choices = zone_choices
        if is_edit:
            self.fields['product_identifier'].widget.attrs['readonly'] = True  # Often postcode can't change
            self.fields['product_identifier'].help_text = "Product Identifier cannot be changed after creation"
            # self.fields['zone_code'].widget.attrs['readonly'] = True  # Often postcode can't change
            self.fields['zone_code'].disabled = True  # Disable the field to make it read-only
            self.fields['zone_code'].required = False # Disabled fields are not sent, so validaton fails if required
            self.fields['zone_code'].help_text = "Zone Code cannot be changed after creation"


class WarehouseForm(forms.Form):
    name = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control','required': 'required'}),
        help_text="e.g., 2000, 3000-3005"
    )
    location = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control','required': 'required'})
    )
    # is_active = forms.BooleanField(
    #     required=False,
    #     initial=True,
    #     widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    # )
    # If you're editing, you might want to hide/show UUID
    uuid = forms.UUIDField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, is_edit=False, **kwargs):
        super().__init__(*args, **kwargs)
        # if is_edit:
            # self.fields['postcode'].widget.attrs['readonly'] = True  # Often postcode can't change
            # self.fields['postcode'].help_text = "Postcode cannot be changed after creation"


class CouponForm(forms.Form):
    code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
        help_text="e.g., SUMMER150"
    )
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
        help_text="e.g., Summer Sale"
    )
    description = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    discount_type = forms.ChoiceField(
        choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'})
    )
    discount_value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'})
    )
    max_discount_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    min_order_value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )


    
    


    # Item selection fields (hidden, populated by JS modals)
    applicable_categories = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    applicable_brands = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    applicable_products = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'required': 'required'})
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'required': 'required'})
    )
    status = forms.ChoiceField(
        choices=[('active', 'Active'), ('inactive', 'Inactive'), ('draft', 'Draft')],
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'})
    )
    # usage_limit = forms.IntegerField(
    #     min_value=0,
    #     required=False,
    #     widget=forms.NumberInput(attrs={'class': 'form-control'})
    # )
    usage_limit = forms.IntegerField(
        min_value=0,
        required=False,
        label="Total Usage Limit",
        help_text="Total number of times this coupon can be used",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    per_user_limit = forms.IntegerField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    uuid = forms.UUIDField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        discount_type = cleaned_data.get("discount_type")
        discount_value = cleaned_data.get("discount_value")

        if discount_type == "percentage" and discount_value is not None:
            if discount_value <= 0 or discount_value > 100:
                self.add_error("discount_value", "Percentage discount must be between 0 and 100.")

        elif discount_type == "fixed" and discount_value is not None:
            if discount_value <= 0:
                self.add_error("discount_value", "Fixed discount value must be greater than 0.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        # category_choices = kwargs.pop('category_choices', [])
        super().__init__(*args, **kwargs)
        # if category_choices:
            # self.fields['applicable_categories'].choices = category_choices

class PromotionCreateForm(forms.Form):
    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")

        min_q = cleaned_data.get("min_quantity")
        max_q = cleaned_data.get("max_quantity")

        discount_type  = cleaned_data.get("discount_type")
        discount_value = cleaned_data.get("discount_value")

        # Date validation
        if start and end and start >= end:
            raise forms.ValidationError("Start date must be before end date")

        # Quantity validation
        if min_q and max_q and min_q > max_q:
            raise forms.ValidationError("Min quantity cannot be greater than max quantity")

        # Discount value validation
        if discount_type == "percentage" and discount_value is not None:
            if discount_value <= 0 or discount_value > 100:
                self.add_error("discount_value", "Percentage discount must be between 0 and 100.")
        elif discount_type == "fixed" and discount_value is not None:
            if discount_value <= 0:
                self.add_error("discount_value", "Fixed discount value must be greater than 0.")

        return cleaned_data

    name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    discount_type = forms.ChoiceField(
        choices=[('fixed', 'Fixed'), ('percentage', 'Percentage')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    discount_value = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    applicable_categories = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    applicable_brands = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    applicable_products = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    min_quantity = forms.IntegerField(
        required=False,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    max_quantity = forms.IntegerField(
        required=False,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    min_order_value = forms.DecimalField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    usage_limit = forms.IntegerField(
        required=False,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    per_user_limit = forms.IntegerField(
        required=False,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    priority = forms.IntegerField(
        required=False,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    start_date = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local','class':'form-control'})
    )

    end_date = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local','class':'form-control'})
    )


class ProductIdRequestForm(forms.Form):
    product_ids = forms.JSONField(required=True)  # Use JSONField for list


class ImportPromotionsForm(forms.Form):
    file = forms.FileField(
        required=True,
        validators=[validate_file_extension, validate_file_size],
        widget=forms.FileInput(
            attrs={
                "accept": ".xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel",
                "class": "form-control"
            }
        ),
        help_text="Upload Excel file (.xlsx or .xls). Maximum size: 10 MB"
    )


class ImportCouponsForm(forms.Form):
    file = forms.FileField(
        required=True,
        validators=[validate_file_extension, validate_file_size],
        widget=forms.FileInput(
            attrs={
                "accept": ".xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel",
                "class": "form-control"
            }
        ),
        help_text="Upload Excel file (.xlsx or .xls). Maximum size: 10 MB"
    )


def validate_file_extension(value):
    if not value.name.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
        raise ValidationError(
            "Unsupported file format. Only CSV, XLS, and XLSX files are allowed."
        )


def validate_file_size(value):
    if value.size > MAX_UPLOAD_SIZE:
        raise ValidationError(
            f"File too large. Maximum allowed size is 10 MB. Your file is {value.size // (1024*1024)} MB."
        )


class ImportReviewsForm(forms.Form):
    file = forms.FileField(required=True, validators=[validate_file_extension, validate_file_size])


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter menu name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter slug (optional)'}),
        }


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['parent', 'title', 'url', 'order', 'status']
        widgets = {
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter URL'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        menu = kwargs.pop('menu', None)
        super().__init__(*args, **kwargs)
        if menu:
            self.instance.menu = menu
            # Filter parent to only show items from the same menu, and exclude self if editing
            queryset = MenuItem.objects.filter(menu=menu)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            self.fields['parent'].queryset = queryset


class ProductHighlightForm(forms.Form):
    product_ids = forms.CharField(
        required=True,
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2Product', 'multiple': 'multiple'})
    )
    banner_image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))




class SocialMediaLinkForm(forms.ModelForm):
    class Meta:
        model = SocialMediaLink
        fields = ["platform", "url", "icon_class", "order", "is_active"]
        widgets = {
            "platform": forms.Select(attrs={"class": "form-select"}),
            "url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://..."}),
            "icon_class": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. bi-facebook (auto-filled if blank)",
                }
            ),
            "order": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "icon_class": "Icon Class (Bootstrap Icons)",
            "order": "Display Order",
        }
        help_texts = {
            "icon_class": "Leave blank to auto-fill based on platform.",
            "order": "Lower numbers appear first.",
        }

class ReturnReasonForm(forms.Form):
    reason = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )