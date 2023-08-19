from rest_framework.test import APITestCase
from django.urls import reverse

from django.contrib.auth.models import User 

from store.models import Product, Tag
from store.serializers import ProductSerializer

# Create your tests here.
class AuthApiViewTestCase(APITestCase):
    def test_register_view_200(self):
        # Correct data
        url = reverse('auth-register')
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get().username, 'test')
        assert 'token' in list(response.data)

    def test_register_view_400(self):
        url = reverse('auth-register')
        # No data
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 400)
        # --- Username tests: ---
        # Empty username
        data = {'username': '',
                'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # No username
        data = {'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # Too long username
        data = {'username': 'test'*200,
                'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # Wrong type of username
        data = {'username': True,
                'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

        # --- Password tests: ---
        # Empty password
        data = {'username': 'test',
                'password': ''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # No password
        data = {'username': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # Too long password
        data = {'username': 'test',
                'password': 'test'*200}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # Wrong type of password
        data = {'username': 'test',
                'password': True}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

        # User already created
        # Create user
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data, format='json')
        # Create the same user again
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_view_200(self):
        # Creating user
        url = reverse('auth-register')
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data, format='json')
        # Correct data
        url = reverse('auth-login')
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'token' in list(response.data)

    def test_login_view_400(self):
        # Creating user
        url = reverse('auth-register')
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data, format='json')

        url = reverse('auth-login')
        # No data
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 400)
        # No username
        data = {'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # No password
        data = {'username': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_view_401(self):
        # Creating user
        url = reverse('auth-register')
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data, format='json')

        url = reverse('auth-login')
        # Wrong password
        data = {'username': 'test',
                'password': 'tset'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)
        # Empty password
        data = {'username': 'test',
                'password': ''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)
        # Wrong type of password
        data = {'username': 'test',
                'password': True}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)
        
    def test_login_view_404(self):
        # User not created
        url = reverse('auth-login')
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 404)
        # Creating user
        url = reverse('auth-register')
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data, format='json')

        url = reverse('auth-login')
        # Empty username
        data = {'username': '',
                'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 404)
        # Wrong type of username
        data = {'username': True,
                'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 404)

    def test_logout_view_200(self):
        # Creating user
        url = reverse('auth-register')
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data, format='json')
        token = response.data['token']
        # Correct token
        url = reverse('auth-logout')
        headers = {'Authorization': 'Token ' + token}
        response = self.client.post(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)

    def test_logout_view_403(self):
        # Creating user
        url = reverse('auth-register')
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data, format='json')
        token = response.data['token']
        url = reverse('auth-logout')
        # Wrong token
        headers = {'Authorization': 'Token 1111'}
        response = self.client.post(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 403)
        # No token
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 403)


class ProductModelViewSetTestCase(APITestCase):
    def set_up(self):
        tag_one = Tag(name='tag1')
        tag_one.save()
        tag_two = Tag(name='tag2')
        tag_two.save()
        tag_three = Tag(name='tag3')
        tag_three.save()

        item_one = Product(
                name='test1',
                price='1.0',
                description='test1',
                vendor_code='test_code1',
                stock=1
        )
        item_one.save()
        item_one.tags.add(tag_one, tag_two, tag_three)
        item_one.save()

        item_two = Product(
                name='test2',
                price='2.0',
                description='test2',
                vendor_code='test_code1',
                stock=2
        )
        item_two.save()
        item_two.tags.add(tag_one, tag_two)
        item_two.save()

        item_three = Product(
                name='test3',
                price='3.0',
                description='test3',
                vendor_code='test_code2',
                stock=3
        )
        item_three.save()
        item_three.tags.add(tag_one)
        item_three.save()

        return item_one, item_two, item_three

    def test_listing(self):
        item_one, item_two, item_three = self.set_up()
        url = reverse('products')
        response = self.client.get(url, format='json')

        # Test view returting all the results
        self.assertEqual(response.data['count'], 3)

        # Test returned products having all the fields
        for product in response.data['results']:
            assert 'id' in list(product)
            assert 'name' in list(product)
            assert 'price' in list(product)
            assert 'description' in list(product)
            assert 'vendor_code' in list(product)
            assert 'stock' in list(product)
            assert 'tags' in list(product)
            for tag in product['tags']:
                assert 'id' in list(tag)
                assert 'name' in list(tag)

    def test_pagination(self):
        item_one, item_two, item_three = self.set_up()
        url = reverse('products')

        # --- Testing page size: ---
        # Invalid page size
        query = {'page_size': 0}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'next' in list(response.data)
        assert 'previous' in list(response.data)
        # Normal page size
        query = {'page_size': 10}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'next' in list(response.data)
        assert 'previous' in list(response.data)
        # Page size too big
        query = {'page_size': 10000}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'next' in list(response.data)
        assert 'previous' in list(response.data)
        # Wrong type of page size
        query = {'page_size': True}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'next' in list(response.data)
        assert 'previous' in list(response.data)
        query = {'page_size': 'test'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'next' in list(response.data)
        assert 'previous' in list(response.data)

        # --- Testing page: ---
        # Valid page
        query = {'page': 3,
                 'page_size': 1}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'next' in list(response.data)
        assert 'previous' in list(response.data)
        query = {'page': 2,
                 'page_size': 2}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'next' in list(response.data)
        assert 'previous' in list(response.data)
        query = {'page': 1,
                 'page_size': 3}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'next' in list(response.data)
        assert 'previous' in list(response.data)
        # Page zero
        query = {'page': 0}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 404)
        # Page number too big
        query = {'page': 10000}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 404)
        # Wrong type of page number
        query = {'page': True}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 404)
        query = {'page': 'test'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 404)

    def test_filtering(self):
        item_one, item_two, item_three = self.set_up()
        url = reverse('products')

        # Testing min_price
        query_params = [
                ('min_price', '0', 3),
                ('min_price', '1', 2),
                ('min_price', '2', 1),
                ('min_price', '3', 0)
        ]
        for param in query_params:
            query_key, query_val, results_count = param
            query = {query_key: query_val}
            response = self.client.get(url, query, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['count'], results_count)
        # Wrong type of min_price
        query = {'min_price': True}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 400)
        query = {'min_price': 'test'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 400)

        # Testing max_price
        query_params = [
                ('max_price', '4', 3),
                ('max_price', '3', 2),
                ('max_price', '2', 1),
                ('max_price', '1', 0)
        ]
        for param in query_params:
            query_key, query_val, results_count = param
            query = {query_key: query_val}
            response = self.client.get(url, query, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['count'], results_count)
        # Wrong type of max_price
        query = {'max_price': True}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 400)
        query = {'max_price': 'test'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 400)

        # Testing stock
        query_params = [
                ('stock', '1', 3),
                ('stock', '2', 2),
                ('stock', '3', 1),
                ('stock', '4', 0)
        ]
        for param in query_params:
            query_key, query_val, results_count = param
            query = {query_key: query_val}
            response = self.client.get(url, query, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['count'], results_count)
        # Wrong type of stock
        query = {'stock': True}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 400)
        query = {'stock': 'test'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 400)

        # --- Testing combination ---
        query = {'min_price': '1', 
                 'max_price': '3'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        query = {'min_price': '3', 
                 'max_price': '1'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

        query = {'stock': '2', 
                 'max_price': '3'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        query = {'stock': '2', 
                 'max_price': '3',
                 'min_price': '1'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        
    def test_ordering(self):
        item_one, item_two, item_three = self.set_up()
        url = reverse('products')

        # The straight ordering
        query_params = ['price', 'name', 'stock']
        for param in query_params:
            for page in range(1, 4):
                query = {'ordering': param,
                         'page': page}
                response = self.client.get(url, query, format='json')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data['results'][0]['name'], 'test'+str(page))
        # The reverse ordering
        query_params = ['-price', '-name', '-stock']
        for param in query_params:
            for page in range(1, 4):
                query = {'ordering': param,
                         'page': 4-page}
                response = self.client.get(url, query, format='json')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data['results'][0]['name'], 'test'+str(page))
        # Invalid ordering parameter
        query = {'ordering': 'test'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)

    def test_tags(self):
        self.set_up()
        url = reverse('products')

        # One tag
        query = {'tags': ['1']}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)
        # Two tags
        query = {'tags': ['1', '2']}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        # Three tags
        query = {'tags': ['1', '2', '3']}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        # Invalid tags
        query = {'tags': 'test'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 400)

    def test_combination(self):
        self.set_up()
        url = reverse('products')

        # One of everything
        query = {'max_price': '3.0',
                 'ordering': '-price',
                 'tags': '2',
                 'page': '2'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['name'], 'test1')


class UsersMeViewTestCase(APITestCase):
    def register(self):
        url = reverse('auth-register')
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data, format='json')

    def login(self):
        url = reverse('auth-login')
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.token = response.data['token']

    def test_users_me_get(self):
        self.register()
        url = reverse('users-me')
        # Unauthorized access
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        # Successful request
        headers = {'Authorization': 'Token ' + self.token}
        response = self.client.get(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'first_name' in response.data
        assert 'last_name' in response.data

    def test_users_me_put(self):
        self.register()
        url = reverse('users-me')
        # Unauthorized access
        data = {'first_name': 'test_name'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        # --- Successful request: ---
        # Set one parameter
        headers = {'Authorization': 'Token ' + self.token}
        data = {'first_name': 'test_name'}
        response = self.client.put(url, data, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'test_name')
        # Set two parameters
        headers = {'Authorization': 'Token ' + self.token}
        data = {'first_name': 'test_name2',
                'last_name': 'test_last_name'}
        response = self.client.put(url, data, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'test_name2')
        self.assertEqual(response.data['last_name'], 'test_last_name')

    def test_users_me_delete(self):
        self.register()
        url = reverse('users-me')
        # Unauthorized access
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        # Successful request
        headers = {'Authorization': 'Token ' + self.token}
        response = self.client.delete(url,headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
        # Check that account was deleted
        self.assertEqual(len(User.objects.all()), 0)


class CartViewSetTestCase(APITestCase):
    def set_up(self):
        item_one = Product(
                name='test1',
                price='1.0',
                description='test1',
                vendor_code='test_code1',
                stock=1
        )
        item_one.save()
        item_two = Product(
                name='test2',
                price='2.0',
                description='test2',
                vendor_code='test_code1',
                stock=2
        )
        item_two.save()
        # Registering
        url = reverse('auth-register')
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data, format='json')

    def login(self):
        url = reverse('auth-login')
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.token = response.data['token']

    def test_cart_put(self):
        self.set_up()
        url = reverse('cart')

        # Unauthorized
        data = {'id': '1',
                'amount': 1}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)
        
        self.login()
        # No data sent
        headers = {'Authorization': 'Token ' + self.token}
        response = self.client.put(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Invalid id
        data = {'id': '100',
                'amount': 1}
        headers = {'Authorization': 'Token ' + self.token}
        response = self.client.put(url, data, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)

        # Successful request
        data = {'id': '1',
                'amount': 1}
        headers = {'Authorization': 'Token ' + self.token}
        response = self.client.put(url, data, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'items' in list(response.data)
        self.assertEqual(response.data['items'][0]['id'], 1)
        # Check amount changes
        response = self.client.put(url, data, headers=headers, format='json')
        self.assertEqual(response.data['items'][0]['amount'], 2)
        # Check cum_price changes
        self.assertEqual(response.data['items'][0]['cum_price'], 2.0)
        self.assertEqual(response.data['cum_price'], '2.00')

        # Put another item
        data = {'id': '2',
                'amount': 10}
        response = self.client.put(url, data, headers=headers, format='json')
        self.assertEqual(response.data['items'][1]['id'], 2)
        self.assertEqual(response.data['items'][1]['amount'], 10)
        self.assertEqual(response.data['items'][1]['cum_price'], 20.0)
        self.assertEqual(response.data['cum_price'], '22.00')

    def test_cart_get(self):
        self.set_up()
        url = reverse('cart')

        # Unauthorized
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        headers = {'Authorization': 'Token ' + self.token}
        # Empty cart
        response = self.client.get(url, headers=headers, format='json')
        self.assertEqual(len(response.data['items']), 0)

        # Setting cart
        data = {'id': '1',
                'amount': 2}
        response = self.client.put(url, data, headers=headers, format='json')
        data = {'id': '2',
                'amount': 10}
        response = self.client.put(url, data, headers=headers, format='json')
        # Successful request
        response = self.client.get(url, headers=headers, format='json')
        self.assertEqual(response.data['items'][1]['id'], 2)
        self.assertEqual(response.data['items'][1]['amount'], 10)
        self.assertEqual(response.data['items'][1]['cum_price'], 20.0)
        self.assertEqual(response.data['cum_price'], '22.00')

    def test_cart_delete(self):
        self.set_up()
        url = reverse('cart')

        # Unauthorized
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        headers = {'Authorization': 'Token ' + self.token}

        # Setting cart
        data = {'id': '1',
                'amount': 2}
        response = self.client.put(url, data, headers=headers, format='json')
        data = {'id': '2',
                'amount': 10}
        response = self.client.put(url, data, headers=headers, format='json')

        # Invlid id
        query = '?id=100'
        response = self.client.delete(url+query, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['items']), 2)
        # Successful request
        query = '?id=1'
        response = self.client.delete(url+query, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['amount'], 1)

        query = '?id=2&amount=2'
        response = self.client.delete(url+query, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][1]['amount'], 8)

        query = '?id=2&amount=ALL'
        response = self.client.delete(url+query, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['amount'], 1)
        self.assertEqual(len(response.data['items']), 1)

        data = {'id': '2',
                'amount': 10}
        response = self.client.put(url, data, headers=headers, format='json')
        response = self.client.delete(url, headers=headers, format='json')
        self.assertEqual(len(response.data['items']), 0)

    def test_cart_checkout(self):
        self.set_up()
        url = reverse('cart-checkout')

        # Unauthorized
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        headers = {'Authorization': 'Token ' + self.token}

        # Setting cart
        url = reverse('cart')
        data = {'id': '1',
                'amount': 2}
        response = self.client.put(url, data, headers=headers, format='json')
        data = {'id': '2',
                'amount': 10}
        response = self.client.put(url, data, headers=headers, format='json')

        url = reverse('cart-checkout')
        # No address provided
        response = self.client.post(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)

        # Successful checkout
        data = {'address': 'test'}
        response = self.client.post(url, data, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
