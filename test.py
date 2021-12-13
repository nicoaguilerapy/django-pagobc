from core.models import Payment
import time

# starting time
start = time.time()

for i in range(0, 100):
    pay = Payment.objects.create(concept = 'test', mount=i)
    pay.concept = 'hola'
    pay.save()
    pay.delete()

end = time.time()
print(f"Ejecutado en {end - start}")