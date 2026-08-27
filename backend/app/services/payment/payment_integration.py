"""
Payment Integration Service (Stub Implementation)

This is a stub implementation for Phase 5. It simulates payment processing
without actual integration to Payme/Click APIs.

For production:
- Implement real Payme Merchant API integration
- Implement real Click Merchant API integration
- Add proper webhook signature verification
- Add retry logic for failed payments
- Add proper error handling and logging
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.payment import Payment, PaymentProvider, PaymentStatus
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.core.exceptions import ValidationException, NotFoundError
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class PaymentIntegration:
    """
    Unified payment integration service
    
    Handles both Payme and Click payment providers with stub implementation.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_payment(
        self,
        order_id: int,
        provider: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """
        Create a new payment transaction
        
        STUB IMPLEMENTATION: Returns a fake payment URL
        
        Args:
            order_id: Order ID
            provider: Payment provider ('payme' or 'click')
            amount: Payment amount
            
        Returns:
            Dict with payment_id, external_id, and payment_url
            
        Raises:
            ValidationException: Invalid provider or amount
            NotFoundError: Order not found
        """
        # Validate provider
        if provider not in ['payme', 'click']:
            raise ValidationException(f"Недопустимый провайдер: {provider}")
        
        # Validate amount
        if amount <= 0:
            raise ValidationException("Сумма должна быть положительной")
        
        # Check order exists
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise NotFoundError(f"Заявка {order_id} не найдена")
        
        # Check order status (should be awaiting_payment)
        if order.status != OrderStatus.AWAITING_PAYMENT:
            raise ValidationException(
                f"Нельзя создать платёж для заявки со статусом {order.status}"
            )
        
        # Generate external_id (unique)
        external_id = f"{provider}_{uuid.uuid4().hex[:16]}"
        
        # Create payment record
        payment = Payment(
            order_id=order_id,
            provider=PaymentProvider(provider),
            amount=amount,
            status=PaymentStatus.PENDING,
            external_id=external_id,
            webhook_data=None
        )
        
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        
        # STUB: Generate fake payment URL
        payment_url = self._generate_stub_payment_url(
            provider, external_id, amount
        )
        
        logger.info(
            f"Payment created (STUB): payment_id={payment.id}, "
            f"order_id={order_id}, provider={provider}, amount={amount}"
        )
        
        return {
            "payment_id": payment.id,
            "external_id": external_id,
            "payment_url": payment_url,
            "provider": provider,
            "amount": float(amount),
            "status": "pending"
        }
    
    def _generate_stub_payment_url(
        self,
        provider: str,
        external_id: str,
        amount: Decimal
    ) -> str:
        """
        Generate stub payment URL for testing
        
        In production, this would call the actual Payme/Click API
        to get a real checkout URL.
        """
        base_url = "http://localhost:8000"  # Change in production
        
        # Stub payment page (would be Payme/Click hosted page in production)
        return f"{base_url}/stub/payment?provider={provider}&id={external_id}&amount={amount}"
    
    async def handle_webhook(
        self,
        provider: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Handle payment webhook from provider
        
        STUB IMPLEMENTATION: Accepts any payload without signature verification
        
        Args:
            provider: Payment provider ('payme' or 'click')
            payload: Webhook payload
            signature: Webhook signature (for verification)
            
        Returns:
            Tuple of (success: bool, message: str)
            
        Raises:
            ValidationException: Invalid webhook data
        """
        # STUB: In production, verify signature here
        if signature:
            logger.info(f"STUB: Skipping signature verification for {provider}")
            # self._verify_signature(provider, payload, signature)
        
        # Extract webhook data
        try:
            external_id = payload.get("external_id") or payload.get("transaction_id")
            status = payload.get("status")
            
            if not external_id or not status:
                raise ValidationException("Webhook: отсутствуют обязательные поля")
            
        except Exception as e:
            logger.error(f"Webhook parsing error: {e}")
            raise ValidationException("Неверный формат webhook")
        
        # Find payment by external_id
        result = await self.db.execute(
            select(Payment)
            .options(selectinload(Payment.order))
            .where(Payment.external_id == external_id)
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            logger.warning(f"Webhook: payment not found for external_id={external_id}")
            return False, "Payment not found"
        
        # Check idempotency: if already processed with same status, return success
        if payment.status.value == status:
            logger.info(f"Webhook: already processed (idempotent) payment_id={payment.id}")
            return True, "Already processed"
        
        # Update payment status and webhook data
        payment.status = self._map_webhook_status(status)
        payment.webhook_data = payload
        
        if payment.status == PaymentStatus.SUCCESS:
            payment.completed_at = datetime.utcnow()
        
        # Update order status if payment successful
        if payment.status == PaymentStatus.SUCCESS:
            await self._update_order_status(payment.order_id, OrderStatus.PAID)
            
            # Send success notifications
            await self._send_payment_success_notifications(payment)
            
            logger.info(
                f"Payment successful: payment_id={payment.id}, "
                f"order_id={payment.order_id}, amount={payment.amount}"
            )
        elif payment.status == PaymentStatus.FAILED:
            # Send failure notifications
            await self._send_payment_failed_notifications(payment)
            
            logger.warning(
                f"Payment failed: payment_id={payment.id}, "
                f"order_id={payment.order_id}"
            )
        
        await self.db.commit()
        
        return True, "Webhook processed"
    
    def _map_webhook_status(self, webhook_status: str) -> PaymentStatus:
        """Map provider webhook status to internal PaymentStatus"""
        status_mapping = {
            "success": PaymentStatus.SUCCESS,
            "paid": PaymentStatus.SUCCESS,
            "completed": PaymentStatus.SUCCESS,
            "failed": PaymentStatus.FAILED,
            "error": PaymentStatus.FAILED,
            "cancelled": PaymentStatus.CANCELLED,
            "canceled": PaymentStatus.CANCELLED,
            "pending": PaymentStatus.PENDING
        }
        
        return status_mapping.get(
            webhook_status.lower(),
            PaymentStatus.FAILED
        )
    
    async def _update_order_status(
        self,
        order_id: int,
        new_status: OrderStatus
    ) -> None:
        """
        Update order status
        
        This should validate status transitions using the state machine
        from OrderManagement service.
        """
        await self.db.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(status=new_status)
        )
    
    async def get_payment_by_order(
        self,
        order_id: int
    ) -> Optional[Payment]:
        """Get latest payment for an order"""
        result = await self.db.execute(
            select(Payment)
            .where(Payment.order_id == order_id)
            .order_by(Payment.created_at.desc())
        )
        return result.scalar_one_or_none()
    
    async def list_payments(
        self,
        order_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[Payment]:
        """List payments with optional filtering"""
        query = select(Payment).options(selectinload(Payment.order))
        
        if order_id:
            query = query.where(Payment.order_id == order_id)
        
        if status:
            query = query.where(Payment.status == PaymentStatus(status))
        
        query = query.order_by(Payment.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def _send_payment_success_notifications(
        self,
        payment: Payment
    ) -> None:
        """Send notifications after successful payment"""
        try:
            # Load order with user and service
            result = await self.db.execute(
                select(Order)
                .options(
                    selectinload(Order.user),
                    selectinload(Order.service)
                )
                .where(Order.id == payment.order_id)
            )
            order = result.scalar_one()
            
            # Notify user
            await NotificationService.notify_payment_success(
                user_phone=order.user.phone,
                user_email=getattr(order.user, 'email', None),
                order_id=order.id,
                amount=payment.amount,
                service_name=order.service.name_ru
            )
            
            # Notify admin (stub - would need admin phone from settings)
            # await NotificationService.notify_admin_new_paid_order(...)
            
        except Exception as e:
            # Don't fail webhook if notifications fail
            logger.error(f"Notification error after payment success: {e}")
    
    async def _send_payment_failed_notifications(
        self,
        payment: Payment
    ) -> None:
        """Send notifications after failed payment"""
        try:
            # Load order with user
            result = await self.db.execute(
                select(Order)
                .options(selectinload(Order.user))
                .where(Order.id == payment.order_id)
            )
            order = result.scalar_one()
            
            # Generate retry payment URL
            payment_url = f"http://localhost:8000/orders/{order.id}"  # Stub
            
            # Notify user
            await NotificationService.notify_payment_failed(
                user_phone=order.user.phone,
                user_email=getattr(order.user, 'email', None),
                order_id=order.id,
                payment_url=payment_url
            )
            
        except Exception as e:
            logger.error(f"Notification error after payment failure: {e}")
