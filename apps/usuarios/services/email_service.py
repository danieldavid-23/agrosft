import logging
import os

import requests
from django.conf import settings

logger = logging.getLogger("apps.usuarios.services.email_service")



def send_password_reset_email(to_email, to_name, reset_link):
    """
    Envía un correo electrónico para restablecer la contraseña a través de la API REST de Brevo.
    Lee BREVO_API_KEY desde os.environ (cargada por python-dotenv desde .env al iniciar Django).
    Utiliza settings.DEFAULT_FROM_EMAIL como remitente verificado en Brevo.
    """
    api_key = os.environ.get('BREVO_API_KEY')
    if not api_key:
        logger.error("No se encontró la variable de entorno BREVO_API_KEY")
        # En entornos de desarrollo sin API key, logueamos el enlace para no bloquear las pruebas locales
        logger.info(f"[DESARROLLO] Enlace de recuperación para {to_email}: {reset_link}")
        return False

    sender_email = settings.DEFAULT_FROM_EMAIL
    sender_name = "AgroSFT"

    # URL de la API de Brevo
    url = "https://api.brevo.com/v3/smtp/email"

    # Cabeceras requeridas por Brevo
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    # Contenido en formato de texto plano
    text_content = (
        f"Hola {to_name},\n\n"
        f"Recibimos una solicitud para restablecer la contraseña asociada a tu cuenta en AGROSFT.\n"
        f"Si fuiste tú, por favor visita el siguiente enlace para elegir una nueva contraseña:\n\n"
        f"{reset_link}\n\n"
        f"Si no solicitaste este cambio, puedes ignorar este correo de forma segura. "
        f"Tu contraseña no cambiará.\n\n"
        f"Atentamente,\n"
        f"El equipo de AGROSFT."
    )

    # Contenido en formato HTML profesional
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Restablecer Contraseña - AgroSFT</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f7f5;
            color: #333333;
            margin: 0;
            padding: 0;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}
        table {{
            border-collapse: collapse !important;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(60,141,60,0.08);
            overflow: hidden;
            border: 1px solid #e1e8e3;
        }}
        .header {{
            background: linear-gradient(135deg, #3C8D3C 0%, #25632C 100%);
            color: #ffffff;
            text-align: center;
            padding: 40px 20px;
        }}
        .header img {{
            width: 48px;
            height: 48px;
            margin-bottom: 12px;
            border: 0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 26px;
            font-weight: 800;
            letter-spacing: 1.5px;
        }}
        .header p {{
            margin: 8px 0 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .content {{
            padding: 40px 30px;
            line-height: 1.7;
        }}
        .content p {{
            margin-bottom: 18px;
            font-size: 15px;
            color: #3d5245;
        }}
        .btn-container {{
            text-align: center;
            margin: 35px 0;
        }}
        .btn {{
            background-color: #3C8D3C;
            color: #ffffff !important;
            text-decoration: none;
            padding: 14px 40px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 16px;
            display: inline-block;
            box-shadow: 0 4px 12px rgba(60, 141, 60, 0.25);
            transition: all 0.3s ease;
        }}
        .security-card {{
            background-color: #f8faf8;
            border-left: 4px solid #3C8D3C;
            padding: 18px;
            margin: 30px 0;
            border-radius: 0 8px 8px 0;
            text-align: left;
        }}
        .security-card h4 {{
            margin: 0 0 10px 0;
            color: #25632C;
            font-size: 15px;
            font-weight: 700;
        }}
        .security-card ul {{
            margin: 0;
            padding-left: 20px;
            font-size: 13px;
            color: #556b5c;
            line-height: 1.6;
        }}
        .divider {{
            border: none;
            border-top: 1px solid #e2ebd9;
            margin: 25px 0;
        }}
        .link-fallback {{
            font-size: 12px;
            color: #7a8a7d;
            word-break: break-all;
            background-color: #f9fbf9;
            padding: 12px;
            border-radius: 6px;
            border: 1px dashed #d6d8cc;
        }}
        .link-fallback a {{
            color: #3C8D3C;
            text-decoration: underline;
        }}
        .footer {{
            background-color: #f7faf7;
            text-align: center;
            padding: 25px 20px;
            font-size: 12px;
            color: #7a8a7d;
            border-top: 1px solid #e2ebd9;
        }}
        .footer p {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://res.cloudinary.com/oxt3bvhj/image/upload/f_auto,q_auto/Logo_j4z26k"
        alt="AgroSFT Logo" width="90"
        style="display:block;margin:auto;">
            <h1>AgroSFT</h1>
            <p>Tecnología y Gestión para el Campo</p>
        </div>
        <div class="content">
            <p>Hola, <strong>{to_name}</strong>:</p>
            <p>Recibimos una solicitud para restablecer la contraseña asociada a tu cuenta en <strong>AgroSFT</strong>.</p>
            <p>Para elegir una nueva contraseña, por favor haz clic en el siguiente botón:</p>
            
            <div class="btn-container">
                <a href="{reset_link}" class="btn">Restablecer mi contraseña</a>
            </div>

            <div class="security-card">
                <h4>🛡️ Recomendaciones de Seguridad:</h4>
                <ul>
                    <li>Este enlace expira pronto y solo sirve para un único uso.</li>
                    <li>Si no has solicitado este cambio, puedes ignorar este mensaje de forma segura. Tu contraseña actual no se modificará.</li>
                    <li>Por tu seguridad, nunca compartas este enlace con nadie. Nuestro equipo de soporte jamás te solicitará contraseñas por correo.</li>
                </ul>
            </div>

            <hr class="divider">
            
            <p class="link-fallback">
                Si tienes problemas con el botón, copia y pega este enlace en tu navegador:<br>
                <a href="{reset_link}">{reset_link}</a>
            </p>
        </div>
        <div class="footer">
            <p>Este es un correo automático. Por favor, no respondas directamente a este mensaje.</p>
            <p>&copy; 2026 AgroSFT &mdash; Todos los derechos reservados.</p>
        </div>
    </div>
</body>
</html>"""

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email
        },
        "to": [
            {
                "email": to_email,
                "name": to_name
            }
        ],
        "subject": "Restablecer contraseña - AGROSFT",
        "htmlContent": html_content,
        "textContent": text_content
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code in [200, 201, 202]:
            logger.info(f"Correo de recuperación enviado exitosamente a {to_email}")
            return True
        else:
            logger.error(
                f"Error de la API de Brevo ({response.status_code}): {response.text}"
            )
            logger.info(
                f"[DESARROLLO - API FAILED] Enlace de recuperación para {to_email}: {reset_link}"
            )
            return False
    except requests.RequestException as e:
        logger.error(f"Error de conexión al enviar correo con Brevo: {str(e)}")
        logger.info(
            f"[DESARROLLO - EXCEPTION] Enlace de recuperación para {to_email}: {reset_link}"
        )
        return False
