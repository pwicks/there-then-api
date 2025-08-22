
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon
from .models import GeographicArea


class MultipleGeographicAreasTestCase(TestCase):
	def setUp(self):
		self.User = get_user_model()
		self.user = self.User.objects.create_user(username="testuser", email="testuser@example.com", password="testpass")

	def test_user_can_create_multiple_geographic_areas(self):
		polygon1 = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
		polygon2 = Polygon(((2, 2), (2, 3), (3, 3), (3, 2), (2, 2)))

		area1 = GeographicArea.objects.create(created_by=self.user, name="Area 1", geometry=polygon1, start_year=2000, end_year=2010)
		area2 = GeographicArea.objects.create(created_by=self.user, name="Area 2", geometry=polygon2, start_year=2011, end_year=2020)

		areas = GeographicArea.objects.filter(created_by=self.user)
		self.assertEqual(areas.count(), 2)
		self.assertIn(area1, areas)
		self.assertIn(area2, areas)
