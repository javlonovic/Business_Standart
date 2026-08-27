class Service {
  final int id;
  final String slug;
  final String nameRu;
  final String? descriptionRu;
  final String? iconUrl;
  final bool isActive;
  final int sortOrder;
  
  Service({
    required this.id,
    required this.slug,
    required this.nameRu,
    this.descriptionRu,
    this.iconUrl,
    required this.isActive,
    required this.sortOrder,
  });
  
  factory Service.fromJson(Map<String, dynamic> json) {
    return Service(
      id: json['id'],
      slug: json['slug'],
      nameRu: json['name_ru'],
      descriptionRu: json['description_ru'],
      iconUrl: json['icon_url'],
      isActive: json['is_active'],
      sortOrder: json['sort_order'],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'slug': slug,
      'name_ru': nameRu,
      'description_ru': descriptionRu,
      'icon_url': iconUrl,
      'is_active': isActive,
      'sort_order': sortOrder,
    };
  }
}
