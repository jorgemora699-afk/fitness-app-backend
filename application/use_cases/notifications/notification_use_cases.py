from domain.entities.membership import Membership
from domain.entities.user import User
from datetime import date, timedelta
import urllib.parse

class GetExpiringMembershipsUseCase:
    def execute(self):
        today = date.today()
        in_5_days = today + timedelta(days=5)

        expiring = Membership.query.filter(
            Membership.is_paid == True,
            Membership.end_date >= today,
            Membership.end_date <= in_5_days
        ).all()

        result = []
        for m in expiring:
            user = User.query.get(m.user_id)
            if user and user.phone:
                phone = ''.join(filter(str.isdigit, user.phone))
                if len(phone) == 10:
                    phone = '57' + phone

                days_left = (m.end_date - today).days

                message = (
                    f"Hola {user.name} 👋, te recordamos que tu membresía "
                    f"vence en {days_left} día(s), el {m.end_date}. "
                    f"Por favor realiza tu pago para seguir disfrutando "
                    f"de tus entrenamientos 💪. "
                    f"Puedes pagar en efectivo o por transferencia. "
                    f"¡Gracias!"
                )
                encoded = urllib.parse.quote(message)
                whatsapp_url = f"https://wa.me/{phone}?text={encoded}"

                result.append({
                    'user': user.to_dict(),
                    'membership': m.to_dict(),
                    'days_left': days_left,
                    'whatsapp_url': whatsapp_url
                })

        return {'expiring': result, 'total': len(result)}, 200