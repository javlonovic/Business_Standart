class EstimateBreakdown {
  final String itemName;
  final String description;
  final double amount;
  
  EstimateBreakdown({
    required this.itemName,
    required this.description,
    required this.amount,
  });
  
  factory EstimateBreakdown.fromJson(Map<String, dynamic> json) {
    return EstimateBreakdown(
      itemName: json['item_name'],
      description: json['description'],
      amount: (json['amount'] as num).toDouble(),
    );
  }
}

class EstimateResult {
  final double total;
  final List<EstimateBreakdown> breakdown;
  final bool isPreliminary;
  final String currency;
  
  EstimateResult({
    required this.total,
    required this.breakdown,
    required this.isPreliminary,
    required this.currency,
  });
  
  factory EstimateResult.fromJson(Map<String, dynamic> json) {
    return EstimateResult(
      total: (json['total'] as num).toDouble(),
      breakdown: (json['breakdown'] as List)
          .map((item) => EstimateBreakdown.fromJson(item))
          .toList(),
      isPreliminary: json['is_preliminary'],
      currency: json['currency'],
    );
  }
  
  /// Форматировать сумму с разделителями тысяч
  String get formattedTotal {
    return total.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (Match m) => '${m[1]} ',
    );
  }
}
