
from django.test import TestCase
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class EmailValidationTests(TestCase):
	def test_email_with_multiple_domain_nodes(self):
		email = 'pwicks@ix.netcom.com'
		try:
			validate_email(email)
		except ValidationError:
			self.fail(f"Email '{email}' should be valid but raised ValidationError.")

# user, created = User.objects.get_or_create(
# 	email="paul.william.wicks+test1@gmail.com",
# 	defaults={"username": "paulwickstest"})
# request_email_verification(user)
