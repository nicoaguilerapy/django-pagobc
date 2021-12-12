from profiles.models import CustomUser

user = CustomUser.objects.create_user(
                                 email='jlennon@beatles.com',
                                 password='glass onion')

print(user)

user.delete()