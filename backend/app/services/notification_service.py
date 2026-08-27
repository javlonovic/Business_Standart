"""
Notification Service (Stub Implementation)

This is a stub implementation for Phase 5. It logs notifications
without actually sending SMS or emails.

For production:
- Implement real SMS gateway integration (playmobile.uz)
- Implement real email sending (SMTP)
- Add retry logic with Celery tasks
- Add notification templates
- Track delivery status
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Notification service for SMS and email
    
    STUB IMPLEMENTATION: Logs notifications instead of sending
    """
    
    @staticmethod
    async def send_sms(
        phone: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send SMS notification
        
        STUB: Logs SMS instead of actually sending
        
        Args:
            phone: Phone number in +998XXXXXXXXX format
            message: SMS text in Russian
            metadata: Additional context (order_id, etc.)
            
        Returns:
            True if successful (always True in stub)
        """
        logger.info(
            f"[SMS STUB] To: {phone}\n"
            f"Message: {message}\n"
            f"Metadata: {metadata}\n"
            f"Timestamp: {datetime.utcnow().isoformat()}"
        )
        
        # In production:
        # - Call SMS gateway API (playmobile.uz)
        # - Handle rate limits
        # - Retry on failure
        # - Track delivery status
        
        return True
    
    @staticmethod
    async def send_email(
        email: str,
        subject: str,
        body: str,
        html: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send email notification
        
        STUB: Logs email instead of actually sending
        
        Args:
            email: Email address
            subject: Email subject
            body: Email body (plain text or HTML)
            html: Whether body is HTML
            metadata: Additional context
            
        Returns:
            True if successful (always True in stub)
        """
        logger.info(
            f"[EMAIL STUB] To: {email}\n"
            f"Subject: {subject}\n"
            f"Body: {body[:100]}...\n"
            f"HTML: {html}\n"
            f"Metadata: {metadata}\n"
            f"Timestamp: {datetime.utcnow().isoformat()}"
        )
        
        # In production:
        # - Use SMTP or email service (SendGrid, AWS SES)
        # - Render HTML templates
        # - Track open/click rates
        # - Handle bounces
        
        return True
    
    @staticmethod
    async def notify_payment_success(
        user_phone: str,
        user_email: Optional[str],
        order_id: int,
        amount: Decimal,
        service_name: str
    ) -> Dict[str, bool]:
        """
        Notify user about successful payment
        
        Sends both SMS and email notifications
        """
        sms_message = (
            f"Business Standart: Оплата принята!\n"
            f"Заявка №{order_id} - {service_name}\n"
            f"Сумма: {amount:,.0f} сум\n"
            f"Статус: Оплачено ✓"
        )
        
        email_body = f"""
Здравствуйте!

Ваша оплата успешно получена.

Заявка: №{order_id}
Услуга: {service_name}
Сумма: {amount:,.0f} сум

Статус заявки изменён на "Оплачено".
Наши специалисты начнут работу в ближайшее время.

С уважением,
Команда Business Standart
+998 (71) 150-15-15
        """
        
        sms_sent = await NotificationService.send_sms(
            phone=user_phone,
            message=sms_message,
            metadata={"type": "payment_success", "order_id": order_id}
        )
        
        email_sent = False
        if user_email:
            email_sent = await NotificationService.send_email(
                email=user_email,
                subject=f"Оплата получена - Заявка №{order_id}",
                body=email_body,
                metadata={"type": "payment_success", "order_id": order_id}
            )
        
        return {"sms": sms_sent, "email": email_sent}
    
    @staticmethod
    async def notify_payment_failed(
        user_phone: str,
        user_email: Optional[str],
        order_id: int,
        payment_url: str
    ) -> Dict[str, bool]:
        """
        Notify user about failed payment
        
        Includes link to retry payment
        """
        sms_message = (
            f"Business Standart: Ошибка оплаты\n"
            f"Заявка №{order_id}\n"
            f"Попробуйте снова: {payment_url}"
        )
        
        email_body = f"""
Здравствуйте!

К сожалению, оплата не прошла.

Заявка: №{order_id}

Пожалуйста, попробуйте оплатить снова:
{payment_url}

Если проблема повторяется, свяжитесь с нами:
+998 (71) 150-15-15
business_standart@mail.ru

С уважением,
Команда Business Standart
        """
        
        sms_sent = await NotificationService.send_sms(
            phone=user_phone,
            message=sms_message,
            metadata={"type": "payment_failed", "order_id": order_id}
        )
        
        email_sent = False
        if user_email:
            email_sent = await NotificationService.send_email(
                email=user_email,
                subject=f"Ошибка оплаты - Заявка №{order_id}",
                body=email_body,
                metadata={"type": "payment_failed", "order_id": order_id}
            )
        
        return {"sms": sms_sent, "email": email_sent}
    
    @staticmethod
    async def notify_document_ready(
        user_phone: str,
        user_email: Optional[str],
        order_id: int,
        service_name: str,
        download_url: str
    ) -> Dict[str, bool]:
        """
        Notify user that document is ready for download
        """
        sms_message = (
            f"Business Standart: Документ готов!\n"
            f"Заявка №{order_id} - {service_name}\n"
            f"Скачать: {download_url}"
        )
        
        email_body = f"""
Здравствуйте!

Ваш документ готов для скачивания.

Заявка: №{order_id}
Услуга: {service_name}

Скачать документ:
{download_url}

Ссылка действительна 7 дней.

С уважением,
Команда Business Standart
+998 (71) 150-15-15
        """
        
        sms_sent = await NotificationService.send_sms(
            phone=user_phone,
            message=sms_message,
            metadata={"type": "document_ready", "order_id": order_id}
        )
        
        email_sent = False
        if user_email:
            email_sent = await NotificationService.send_email(
                email=user_email,
                subject=f"Документ готов - Заявка №{order_id}",
                body=email_body,
                metadata={"type": "document_ready", "order_id": order_id}
            )
        
        return {"sms": sms_sent, "email": email_sent}
    
    @staticmethod
    async def notify_admin_new_paid_order(
        admin_phone: str,
        order_id: int,
        user_name: str,
        service_name: str,
        amount: Decimal
    ) -> bool:
        """
        Notify admin about new paid order
        """
        message = (
            f"Business Standart: Новая заявка!\n"
            f"№{order_id} - {service_name}\n"
            f"Клиент: {user_name}\n"
            f"Сумма: {amount:,.0f} сум"
        )
        
        return await NotificationService.send_sms(
            phone=admin_phone,
            message=message,
            metadata={
                "type": "admin_new_order",
                "order_id": order_id
            }
        )
