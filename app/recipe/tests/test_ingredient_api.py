from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """Test the publicly avauilable ingredient API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test ingredients can be retireived by authorized users"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='danish21752@gmail.com',
            password='danish123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retieve_ingredients_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Carrot')
        Ingredient.objects.create(user=self.user, name='Banana')

        res = self.client.get(INGREDIENT_URL)

        ingredient = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredient, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test that ingredient for the authentocatesd user are returned"""
        user2 = get_user_model().objects.create_user(
            email='danish21642@gmail.com',
            password='test123'
        )
        Ingredient.objects.create(user=user2, name='Sugar')
        ingredient = Ingredient.objects.create(user=self.user, name='Candy')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successfull(self):
        """Test creating a new ingredient"""
        payload = {
            'name': 'New Ingredient'
        }

        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_invlid_ingredient(self):
        """Test creating a new ingredient with invalid payload"""
        payload = {'name': ''}

        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
