import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../services/api_service.dart';
import '../providers/auth_provider.dart';

/// Экран выбора способа оплаты и обработки платежа
class PaymentScreen extends StatefulWidget {
  final int orderId;
  final double amount;

  const PaymentScreen({
    super.key,
    required this.orderId,
    required this.amount,
  });

  @override
  State<PaymentScreen> createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  String? _selectedProvider;
  bool _isProcessing = false;
  String? _error;
  String? _externalId;

  final ApiService _apiService = ApiService();

  Future<void> _createPayment() async {
    if (_selectedProvider == null) {
      setState(() {
        _error = 'Выберите способ оплаты';
      });
      return;
    }

    setState(() {
      _isProcessing = true;
      _error = null;
    });

    try {
      // Get API service with token
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      _apiService.setToken(authProvider.token);

      // Create payment
      final paymentData = await _apiService.createPayment(
        orderId: widget.orderId,
        provider: _selectedProvider!,
      );

      setState(() {
        _externalId = paymentData['external_id'];
      });

      // In production: redirect to payment_url
      // For stub: show test payment dialog
      if (mounted) {
        _showTestPaymentDialog(paymentData);
      }
    } catch (e) {
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _isProcessing = false;
      });
    }
  }

  void _showTestPaymentDialog(Map<String, dynamic> paymentData) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Тестовый платёж'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Это тестовая реализация платёжной системы.\n',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            Text('Провайдер: ${paymentData['provider']}'),
            Text('Сумма: ${paymentData['amount']} сум'),
            Text('ID: ${paymentData['external_id']}'),
            const SizedBox(height: 16),
            const Text('Выберите результат оплаты:'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _simulatePayment(paymentData['external_id'], false);
            },
            child: const Text(
              'Провал',
              style: TextStyle(color: Colors.red),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _simulatePayment(paymentData['external_id'], true);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
            ),
            child: const Text('Успех'),
          ),
        ],
      ),
    );
  }

  Future<void> _simulatePayment(String externalId, bool success) async {
    setState(() {
      _isProcessing = true;
    });

    try {
      // Simulate payment webhook
      if (success) {
        await _apiService.simulatePaymentSuccess(externalId);
      } else {
        await _apiService.simulatePaymentFailure(externalId);
      }

      // Wait a bit for webhook processing
      await Future.delayed(const Duration(seconds: 1));

      if (mounted) {
        if (success) {
          _showSuccessDialog();
        } else {
          _showFailureDialog();
        }
      }
    } catch (e) {
      setState(() {
        _error = 'Ошибка симуляции: ${e.toString()}';
        _isProcessing = false;
      });
    }
  }

  void _showSuccessDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.check_circle, color: Colors.green.shade600, size: 32),
            const SizedBox(width: 12),
            const Text('Оплата успешна'),
          ],
        ),
        content: const Text(
          'Платёж успешно обработан.\n'
          'Статус заявки обновлён на "Оплачено".',
        ),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              Navigator.pop(context, true); // Return to order details with success
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.accentColor,
            ),
            child: const Text('Вернуться к заявке'),
          ),
        ],
      ),
    );
  }

  void _showFailureDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.error_outline, color: AppTheme.errorColor, size: 32),
            const SizedBox(width: 12),
            const Text('Ошибка оплаты'),
          ],
        ),
        content: const Text(
          'К сожалению, платёж не прошёл.\n'
          'Попробуйте ещё раз или выберите другой способ оплаты.',
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              Navigator.pop(context, false); // Return to order details
            },
            child: const Text('Отмена'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              setState(() {
                _selectedProvider = null;
                _isProcessing = false;
                _externalId = null;
              });
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.accentColor,
            ),
            child: const Text('Попробовать снова'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      appBar: AppBar(
        title: const Text('Оплата заявки'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
      ),
      body: _isProcessing && _externalId != null
          ? _buildProcessingView()
          : _buildPaymentSelectionView(),
    );
  }

  Widget _buildProcessingView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 24),
          Text(
            'Обработка платежа...',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Text(
            'Пожалуйста, подождите',
            style: TextStyle(color: AppTheme.textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildPaymentSelectionView() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 600),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Order info
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Заявка №${widget.orderId}',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Сумма к оплате:',
                            style: TextStyle(
                              fontSize: 16,
                              color: AppTheme.textSecondary,
                            ),
                          ),
                          Text(
                            '${widget.amount.toStringAsFixed(0)} сум',
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: AppTheme.primaryColor,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 32),

              // Payment method selection
              Text(
                'Выберите способ оплаты',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 16),

              // Payme option
              _buildPaymentOption(
                provider: 'payme',
                title: 'Payme',
                description: 'Uzcard, Humo, Visa, Mastercard',
                icon: Icons.credit_card,
              ),

              const SizedBox(height: 12),

              // Click option
              _buildPaymentOption(
                provider: 'click',
                title: 'Click',
                description: 'Uzcard, Humo',
                icon: Icons.payment,
              ),

              if (_error != null) ...[
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppTheme.errorColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.error_outline, color: AppTheme.errorColor),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          _error!,
                          style: TextStyle(color: AppTheme.errorColor),
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              const SizedBox(height: 32),

              // Pay button
              SizedBox(
                height: 56,
                child: ElevatedButton(
                  onPressed: _isProcessing ? null : _createPayment,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.accentColor,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _isProcessing
                      ? const SizedBox(
                          height: 24,
                          width: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation(Colors.white),
                          ),
                        )
                      : const Text(
                          'Оплатить',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                ),
              ),

              const SizedBox(height: 16),

              // Info text
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline, color: Colors.blue.shade700),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Безопасная оплата через проверенные платёжные системы',
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.blue.shade700,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPaymentOption({
    required String provider,
    required String title,
    required String description,
    required IconData icon,
  }) {
    final isSelected = _selectedProvider == provider;

    return InkWell(
      onTap: () {
        setState(() {
          _selectedProvider = provider;
          _error = null;
        });
      },
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(
            color: isSelected ? AppTheme.accentColor : Colors.grey.shade300,
            width: isSelected ? 2 : 1,
          ),
          borderRadius: BorderRadius.circular(12),
          color: isSelected
              ? AppTheme.accentColor.withOpacity(0.05)
              : Colors.white,
        ),
        child: Row(
          children: [
            Icon(
              icon,
              size: 32,
              color: isSelected ? AppTheme.accentColor : Colors.grey.shade600,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: isSelected
                          ? AppTheme.accentColor
                          : AppTheme.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    description,
                    style: TextStyle(
                      fontSize: 13,
                      color: AppTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            if (isSelected)
              Icon(
                Icons.check_circle,
                color: AppTheme.accentColor,
                size: 28,
              )
            else
              Icon(
                Icons.radio_button_unchecked,
                color: Colors.grey.shade400,
                size: 28,
              ),
          ],
        ),
      ),
    );
  }
}
