class Order {
  final int id;
  final int userId;
  final int serviceId;
  final Map<String, dynamic> params;
  final double estimateTotal;
  final String status;
  final DateTime createdAt;
  final DateTime? deadline;
  final String? documentUrl;
  
  Order({
    required this.id,
    required this.userId,
    required this.serviceId,
    required this.params,
    required this.estimateTotal,
    required this.status,
    required this.createdAt,
    this.deadline,
    this.documentUrl,
  });
  
  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'],
      userId: json['user_id'],
      serviceId: json['service_id'],
      params: json['params'],
      estimateTotal: (json['estimate_total'] as num).toDouble(),
      status: json['status'],
      createdAt: DateTime.parse(json['created_at']),
      deadline: json['deadline'] != null ? DateTime.parse(json['deadline']) : null,
      documentUrl: json['document_url'],
    );
  }
  
  /// Получить читаемое название статуса на русском
  String get statusRu {
    switch (status) {
      case 'draft':
        return 'Черновик';
      case 'awaiting_payment':
        return 'Ожидает оплаты';
      case 'paid':
        return 'Оплачено';
      case 'in_progress':
        return 'В работе';
      case 'ready':
        return 'Готово';
      case 'delivered':
        return 'Выдан';
      case 'cancelled':
        return 'Отменён';
      default:
        return status;
    }
  }
}
