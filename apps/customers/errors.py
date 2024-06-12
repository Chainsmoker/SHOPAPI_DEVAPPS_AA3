class Error:
    TOO_SHORT = {'code': 'TOO_SHORT', 'message': 'La contraseña es muy corta.'}
    INVALID_EMAIL = {'code': 'INVALID_EMAIL', 'message': 'El correo electrónico no es válido.'}
    EMAIL_IN_USE = {'code': 'EMAIL_TAKEN', 'message': 'El correo electrónico ya está en uso.'}