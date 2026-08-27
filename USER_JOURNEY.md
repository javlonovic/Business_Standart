# 👤 User Journey - Business Standart Platform

Visual guide showing the complete user experience flow.

---

## 🎯 Complete User Journey

```
┌─────────────────────────────────────────────────────────┐
│                    START: Homepage                       │
│              http://localhost:8080                       │
│                                                          │
│  • View 9 services                                       │
│  • See currency rates widget                             │
│  • Navigation: Home | About | Services | Contacts       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├─> [Browse Services] ──> Services page
                   ├─> [View About] ──> About page
                   ├─> [Check Rates] ──> Currency archive
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│              Calculator (Guest Access)                   │
│         http://localhost:8080/calculator                 │
│                                                          │
│  1. Select service (dropdown)                            │
│  2. Form appears with dynamic fields                     │
│  3. Enter parameters (area, floors, etc.)                │
│  4. Click "Рассчитать стоимость"                        │
│  5. View estimate with total amount                      │
│  6. Click "Посмотреть детализацию" for breakdown       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│        Click "Создать заявку" (Create Order)            │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├─> Not Logged In?
                   │   │
                   │   ▼
                   │  ┌───────────────────────────────────┐
                   │  │  Dialog: "Требуется авторизация"  │
                   │  │  Options: [Отмена] [Войти]        │
                   │  └──────────┬────────────────────────┘
                   │             │
                   │             ├─> Click "Войти"
                   │             │
                   │             ▼
                   │  ┌─────────────────────────────────┐
                   │  │    Login Screen                  │
                   │  │  /login                          │
                   │  │                                  │
                   │  │  • Phone: +998XXXXXXXXX          │
                   │  │  • Password: ••••••••            │
                   │  │  • [Войти]                       │
                   │  │  • Link to registration          │
                   │  └──────────┬───────────────────────┘
                   │             │
                   │             ├─> New User?
                   │             │
                   │             ▼
                   │  ┌─────────────────────────────────┐
                   │  │  Registration Screen             │
                   │  │  /register                       │
                   │  │                                  │
                   │  │  • Phone: +998XXXXXXXXX          │
                   │  │  • Password: ••••••••            │
                   │  │  • Confirm: ••••••••             │
                   │  │  • Full Name: _______            │
                   │  │  • [Зарегистрироваться]         │
                   │  └──────────┬───────────────────────┘
                   │             │
                   │             ▼
                   │     JWT Token Received
                   │     Session Saved
                   │             │
                   ├─────────────┘
                   │
                   ▼ (Logged In)
┌─────────────────────────────────────────────────────────┐
│                 Order Created!                           │
│         Redirect to Order Details                        │
│      /order-details?id={order_id}                        │
│                                                          │
│  Information Card:                                       │
│  • Order #XXX                                            │
│  • Status: "Ожидает оплаты" (orange badge)             │
│  • Service: "Оценка квартиры"                           │
│  • Amount: 1,500,000 сум                                │
│  • Created: 27.08.2026                                   │
│  • Deadline: 30.08.2026                                  │
│                                                          │
│  Breakdown (if available):                               │
│  • Base fee: 500,000 сум                                │
│  • Area calculation: 1,000,000 сум                      │
│  • Total: 1,500,000 сум                                 │
│                                                          │
│  [Оплатить] ← Big green button                         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼ Click "Оплатить"
┌─────────────────────────────────────────────────────────┐
│              Payment Screen                              │
│         /payment?orderId=X&amount=Y                      │
│                                                          │
│  Order Info Card:                                        │
│  • Заявка №XXX                                          │
│  • Сумма к оплате: 1,500,000 сум                        │
│                                                          │
│  Payment Method Selection:                               │
│  ┌─────────────────────────────────┐                    │
│  │ ○ Payme                          │  (clickable card) │
│  │   Uzcard, Humo, Visa, MC         │                    │
│  └─────────────────────────────────┘                    │
│  ┌─────────────────────────────────┐                    │
│  │ ● Click                          │  (selected)        │
│  │   Uzcard, Humo                   │                    │
│  └─────────────────────────────────┘                    │
│                                                          │
│  [Оплатить] ← Big button                               │
│                                                          │
│  ℹ Безопасная оплата через проверенные                  │
│    платёжные системы                                     │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼ Click "Оплатить"
┌─────────────────────────────────────────────────────────┐
│          Test Payment Dialog (Stub)                      │
│                                                          │
│  "Это тестовая реализация платёжной системы"            │
│                                                          │
│  Провайдер: click                                        │
│  Сумма: 1,500,000 сум                                   │
│  ID: click_abc123...                                     │
│                                                          │
│  Выберите результат оплаты:                              │
│  [Провал]  [Успех] ← Choose outcome                     │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├─> Click "Успех"
                   │   │
                   │   ▼
                   │  ┌───────────────────────────────────┐
                   │  │  ✓ Оплата успешна                  │
                   │  │                                    │
                   │  │  Платёж успешно обработан.         │
                   │  │  Статус заявки обновлён на         │
                   │  │  "Оплачено".                       │
                   │  │                                    │
                   │  │  [Вернуться к заявке]             │
                   │  └──────────┬────────────────────────┘
                   │             │
                   ├─────────────┘
                   │
                   ├─> Click "Провал"
                   │   │
                   │   ▼
                   │  ┌───────────────────────────────────┐
                   │  │  ✗ Ошибка оплаты                   │
                   │  │                                    │
                   │  │  К сожалению, платёж не прошёл.    │
                   │  │  Попробуйте ещё раз.               │
                   │  │                                    │
                   │  │  [Отмена] [Попробовать снова]     │
                   │  └──────────┬────────────────────────┘
                   │             │
                   │             └─> Back to payment screen
                   │
                   ▼ (Payment Successful)
┌─────────────────────────────────────────────────────────┐
│         Order Details (Updated Status)                   │
│      /order-details?id={order_id}                        │
│                                                          │
│  • Status: "Оплачено" ✓ (green badge)                  │
│  • Payment completed                                     │
│  • Order history updated with status change              │
│                                                          │
│  Status History:                                         │
│  ├─ Создана (27.08.2026 14:30)                         │
│  ├─ Ожидает оплаты (27.08.2026 14:30)                  │
│  └─ Оплачено (27.08.2026 14:35) ← NEW                  │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼ Navigate to Cabinet
┌─────────────────────────────────────────────────────────┐
│              Cabinet Screen                              │
│         /cabinet (User Dashboard)                        │
│                                                          │
│  Tabs: [Мои заявки] [Профиль]                          │
│                                                          │
│  Filter by status (chips):                               │
│  [Все] [Черновик] [Ожидает оплаты]                     │
│  [Оплачено] [В работе] [Готово] [Доставлено]           │
│                                                          │
│  Order Cards:                                            │
│  ┌─────────────────────────────────────────────┐        │
│  │ Заявка #XXX        Status: Оплачено ✓       │        │
│  │ Оценка квартиры                              │        │
│  │ Сумма: 1,500,000 сум                        │        │
│  │ Создана: 27.08.2026                          │        │
│  │ Срок: 30.08.2026                             │        │
│  └─────────────────────────────────────────────┘        │
│  (click to view details)                                 │
│                                                          │
│  Profile Tab:                                            │
│  • Name: Test User                                       │
│  • Phone: +998901234567                                  │
│  • [Выйти] ← Logout button                              │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
            User can now:
            • Create more orders
            • Track all orders
            • View order history
            • Use any platform feature

┌─────────────────────────────────────────────────────────┐
│                  END: Order Complete                     │
│                                                          │
│  ✅ User successfully:                                  │
│     • Registered and logged in                           │
│     • Calculated service cost                            │
│     • Created an order                                   │
│     • Completed payment (simulated)                      │
│     • Tracked order status                               │
└─────────────────────────────────────────────────────────┘
```

---

## 🎨 Key UI Elements

### Navigation Bar (All Pages)
```
┌────────────────────────────────────────────────────────────┐
│ Business Standart    Home  About  Services  Contacts       │
│                                                 Calculator │
│                                            [Войти] or      │
│                                            [👤 Username]   │
└────────────────────────────────────────────────────────────┘
```

### Status Badges
- 🟢 **Оплачено** (Paid) - Green
- 🟠 **Ожидает оплаты** (Awaiting Payment) - Orange  
- 🔵 **В работе** (In Progress) - Blue
- 🟣 **Готово** (Ready) - Purple
- 🟢 **Доставлено** (Delivered) - Green
- ⚪ **Черновик** (Draft) - Grey
- 🔴 **Отменено** (Cancelled) - Red

---

## 📱 Mobile Responsive

All screens are responsive and work on:
- 📱 Mobile (360px+)
- 📱 Tablet (768px+)
- 💻 Desktop (1024px+)
- 🖥️ Large screens (1440px+)

---

## 🔄 Alternative Flows

### Flow 1: Direct Login
```
Homepage → Login → Calculator → Order → Payment
```

### Flow 2: Browse First
```
Homepage → Services → About → Calculator → Register → Order
```

### Flow 3: Return User
```
Homepage → (Auto-login via token) → Cabinet → View orders
```

---

## 🧪 Testing Each Screen

| Screen | What to Test | Expected Result |
|--------|-------------|-----------------|
| **Homepage** | Load page | Services + currency rates visible |
| **Calculator** | Select service, calculate | Estimate displayed |
| **Register** | Fill form, submit | Redirect to cabinet |
| **Login** | Enter credentials | Redirect to cabinet |
| **Cabinet** | View orders list | All user orders shown |
| **Order Details** | Click on order | Full details + status history |
| **Payment** | Select provider, pay | Status updates to "paid" |

---

## 💡 Tips for Testing

1. **Use Chrome DevTools** (F12) to:
   - View network requests
   - Check console for errors
   - Test responsive design
   - Monitor performance

2. **Test Multiple Scenarios**:
   - Success payment
   - Failed payment
   - Create multiple orders
   - Filter orders by status
   - Logout and login again

3. **Check Session Persistence**:
   - Login
   - Refresh page
   - Should still be logged in

4. **Test Error Handling**:
   - Wrong password
   - Duplicate phone registration
   - Invalid calculator inputs

---

## ✅ Success Criteria

Complete user journey works if:

- ✅ Can navigate all pages
- ✅ Can register and login
- ✅ Session persists across refreshes
- ✅ Calculator produces estimates
- ✅ Can create orders
- ✅ Orders appear in cabinet
- ✅ Payment changes status
- ✅ Status history is tracked
- ✅ UI is responsive
- ✅ No console errors

---

**Ready to test? Follow [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md)!** 🚀
