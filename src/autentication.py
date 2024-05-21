import time
import pyotp
import qrcode

# Generar una clave secreta
key = "Asdmnnmcdklñoquhfabdisahj"

# Crear un URI de aprovisionamiento
uri = pyotp.totp.TOTP(key).provisioning_uri(name='jascmen', issuer_name='Secure App')

# Generar un código QR a partir del URI
img = qrcode.make(uri)

# Guardar el código QR en un archivo
img.save('qrcode.png')


# Generar un código TOTP
totp = pyotp.TOTP(key)

while True:
    user_code = input("Ingrese el código: ")
    if totp.verify(user_code):
        print("¡Autenticación exitosa!")
        break
    else:
        print("Código incorrecto. Inténtalo de nuevo.")