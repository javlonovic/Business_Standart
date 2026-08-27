import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../models/service.dart';
import '../models/estimate_result.dart';
import '../providers/services_provider.dart';
import '../providers/auth_provider.dart';
import '../services/api_service.dart';
import '../widgets/app_bar_widget.dart';
import '../widgets/footer_widget.dart';

/// Экран калькулятора для расчёта стоимости услуг
class CalculatorScreen extends StatefulWidget {
  const CalculatorScreen({super.key});

  @override
  State<CalculatorScreen> createState() => _CalculatorScreenState();
}

class _CalculatorScreenState extends State<CalculatorScreen> {
  Service? _selectedService;
  Map<String, dynamic>? _serviceParams;
  final Map<String, dynamic> _formValues = {};
  bool _isLoadingParams = false;
  bool _isCalculating = false;
  String? _paramsError;
  EstimateResult? _result;
  String? _calculationError;
  bool _isCreatingOrder = false;

  final ApiService _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ServicesProvider>().loadServices();
    });
  }

  Future<void> _loadServiceParams(int serviceId) async {
    setState(() {
      _isLoadingParams = true;
      _paramsError = null;
      _serviceParams = null;
      _formValues.clear();
      _result = null;
      _calculationError = null;
    });

    try {
      final params = await _apiService.getServiceParams(serviceId);
      setState(() {
        _serviceParams = params;
        _isLoadingParams = false;
      });
    } catch (e) {
      setState(() {
        _paramsError = e.toString().replaceAll('Exception: ', '');
        _isLoadingParams = false;
      });
    }
  }

  Future<void> _calculateEstimate() async {
    if (_selectedService == null) return;

    setState(() {
      _isCalculating = true;
      _calculationError = null;
      _result = null;
    });

    try {
      final result = await _apiService.calculateEstimate(
        serviceId: _selectedService!.id,
        params: _formValues,
      );
      setState(() {
        _result = result;
        _isCalculating = false;
      });
    } catch (e) {
      setState(() {
        _calculationError = e.toString().replaceAll('Exception: ', '');
        _isCalculating = false;
      });
    }
  }

  Future<void> _createOrder() async {
    if (_result == null || _selectedService == null) return;

    // Check authentication
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    if (!authProvider.isAuthenticated) {
      // Redirect to login
      final shouldLogin = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Требуется авторизация'),
          content: const Text(
            'Для создания заявки необходимо войти в систему. Перейти на страницу входа?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Отмена'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Войти'),
            ),
          ],
        ),
      );

      if (shouldLogin == true && mounted) {
        Navigator.pushNamed(context, '/login');
      }
      return;
    }

    setState(() {
      _isCreatingOrder = true;
    });

    try {
      final order = await _apiService.createOrder(
        serviceId: _selectedService!.id,
        params: _formValues,
        estimateTotal: _result!.total,
      );

      if (mounted) {
        // Show success message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Заявка №${order.id} успешно создана'),
            backgroundColor: Colors.green,
          ),
        );

        // Navigate to order details
        Navigator.pushNamed(
          context,
          '/order-details',
          arguments: order.id,
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Ошибка создания заявки: ${e.toString().replaceAll('Exception: ', '')}',
            ),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isCreatingOrder = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      appBar: const AppBarWidget(),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildPageHeader(context),
            _buildCalculatorContent(context),
            const FooterWidget(),
          ],
        ),
      ),
    );
  }

  Widget _buildPageHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 48, 24, 24),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1200),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Калькулятор стоимости',
                style: Theme.of(context).textTheme.displayMedium,
              ),
              const SizedBox(height: 8),
              Text(
                'Рассчитайте предварительную стоимость оценочных услуг онлайн',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCalculatorContent(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 0, 24, 48),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 800),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildServiceSelector(context),
              if (_selectedService != null) ...[
                const SizedBox(height: 32),
                _buildParamsForm(context),
              ],
              if (_result != null) ...[
                const SizedBox(height: 32),
                _buildResult(context),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildServiceSelector(BuildContext context) {
    return Consumer<ServicesProvider>(
      builder: (context, provider, _) {
        if (provider.isLoading) {
          return const Center(child: CircularProgressIndicator());
        }

        if (provider.error != null) {
          return _buildError('Ошибка загрузки услуг', provider.error!);
        }

        final services = provider.services;
        if (services.isEmpty) {
          return _buildError('Услуги не найдены', 'Список услуг пуст');
        }

        return Card(
          elevation: 2,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Выберите услугу',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<Service>(
                  value: _selectedService,
                  decoration: InputDecoration(
                    hintText: 'Выберите услугу из списка',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 16,
                    ),
                  ),
                  items: services.map((service) {
                    return DropdownMenuItem(
                      value: service,
                      child: Text(service.nameRu),
                    );
                  }).toList(),
                  onChanged: (service) {
                    if (service != null) {
                      setState(() => _selectedService = service);
                      _loadServiceParams(service.id);
                    }
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildParamsForm(BuildContext context) {
    if (_isLoadingParams) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(48),
          child: Center(child: CircularProgressIndicator()),
        ),
      );
    }

    if (_paramsError != null) {
      return _buildError('Ошибка загрузки параметров', _paramsError!);
    }

    if (_serviceParams == null) {
      return const SizedBox.shrink();
    }

    final params = _serviceParams!['params'] as List;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Параметры объекта',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 24),
            ...params.map((param) => _buildFormField(param)),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: _isCalculating ? null : _calculateEstimate,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryColor,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: _isCalculating
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation(Colors.white),
                        ),
                      )
                    : const Text(
                        'Рассчитать стоимость',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
              ),
            ),
            if (_calculationError != null) ...[
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
                        _calculationError!,
                        style: TextStyle(color: AppTheme.errorColor),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildFormField(Map<String, dynamic> param) {
    final String key = param['key'];
    final String label = param['label'];
    final String type = param['type'];
    final bool required = param['required'] ?? true;
    final String? hint = param['hint'];

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
              if (required)
                const Text(
                  ' *',
                  style: TextStyle(color: Colors.red),
                ),
            ],
          ),
          if (hint != null) ...[
            const SizedBox(height: 4),
            Text(
              hint,
              style: TextStyle(
                fontSize: 12,
                color: AppTheme.textSecondary,
              ),
            ),
          ],
          const SizedBox(height: 8),
          if (type == 'number')
            TextFormField(
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                hintText: 'Введите значение',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
              ),
              onChanged: (value) {
                _formValues[key] = value.isEmpty ? null : num.tryParse(value);
              },
            )
          else if (type == 'boolean')
            CheckboxListTile(
              value: _formValues[key] ?? false,
              onChanged: (value) {
                setState(() {
                  _formValues[key] = value ?? false;
                });
              },
              title: Text('Да'),
              contentPadding: EdgeInsets.zero,
              controlAffinity: ListTileControlAffinity.leading,
            )
          else if (type == 'select')
            DropdownButtonFormField<String>(
              value: _formValues[key],
              decoration: InputDecoration(
                hintText: 'Выберите значение',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
              ),
              items: (param['options'] as List).map((option) {
                return DropdownMenuItem(
                  value: option['value'],
                  child: Text(option['label']),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  _formValues[key] = value;
                });
              },
            ),
        ],
      ),
    );
  }

  Widget _buildResult(BuildContext context) {
    if (_result == null) return const SizedBox.shrink();

    final formatter = NumberFormat('#,##0', 'ru_RU');

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      color: AppTheme.primaryColor.withOpacity(0.05),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.check_circle, color: Colors.green.shade600, size: 32),
                const SizedBox(width: 12),
                Text(
                  'Предварительная стоимость',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              '${formatter.format(_result!.total)} ${_result!.currency}',
              style: Theme.of(context).textTheme.displayMedium?.copyWith(
                    color: AppTheme.primaryColor,
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: TextButton.icon(
                    onPressed: () => _showBreakdownModal(context),
                    icon: const Icon(Icons.info_outline),
                    label: const Text('Посмотреть детализацию'),
                    style: TextButton.styleFrom(
                      foregroundColor: AppTheme.primaryColor,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isCreatingOrder ? null : _createOrder,
                    icon: _isCreatingOrder
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation(Colors.white),
                            ),
                          )
                        : const Icon(Icons.add_shopping_cart),
                    label: Text(_isCreatingOrder ? 'Создание...' : 'Создать заявку'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.accentColor,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 24,
                        vertical: 12,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showBreakdownModal(BuildContext context) {
    if (_result == null) return;

    final formatter = NumberFormat('#,##0', 'ru_RU');

    showDialog(
      context: context,
      builder: (context) => Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Container(
          constraints: const BoxConstraints(maxWidth: 600),
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Детализация расчёта',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.close),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              ..._result!.breakdown.map((item) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.itemName,
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        item.description,
                        style: TextStyle(
                          fontSize: 13,
                          color: AppTheme.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${formatter.format(item.amount)} ${_result!.currency}',
                        style: const TextStyle(
                          fontWeight: FontWeight.w500,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
              const Divider(height: 32),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Итого:',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  Text(
                    '${formatter.format(_result!.total)} ${_result!.currency}',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: AppTheme.primaryColor,
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildError(String title, String message) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Icon(Icons.error_outline, size: 48, color: AppTheme.errorColor),
            const SizedBox(height: 16),
            Text(
              title,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
