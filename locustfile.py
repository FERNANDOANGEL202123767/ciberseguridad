from locust import HttpUser, task, between
import random
import string

def random_username():
    return ''.join(random.choices(string.ascii_lowercase, k=8))

def random_email():
    return f"{random_username()}@gmail.com"

class WebsiteUser(HttpUser):
    wait_time = between(1, 2)
    host = "http://192.168.63.31"

    @task(2)
    def register(self):
        username = random_username()
        email = random_email()
        password = "Test1234"

        with self.client.post(
            "/api-usuarios/api/auth/register",
            json={"email": username + "@gmail.com","password": password, "name": username},
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 409:
                response.failure("Usuario ya existe (duplicado)")
            elif response.status_code == 404:
                response.failure("Endpoint no encontrado (404)")
            else:
                response.failure(f"Error inesperado: {response.status_code}")
