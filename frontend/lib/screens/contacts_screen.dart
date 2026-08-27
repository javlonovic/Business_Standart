import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../widgets/app_bar_widget.dart';
import '../widgets/footer_widget.dart';

class ContactsScreen extends StatelessWidget {
  const ContactsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      appBar: const AppBarWidget(),
      body: SingleChildScrollView(
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 900),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Контакты',
                        style: Theme.of(context).textTheme.displayMedium,
                      ),
                      const SizedBox(height: 48),
                      _buildContactCard(
                        context,
                        icon: Icons.phone,
                        title: 'Телефоны',
                        items: [
                          ContactItem('Городской', '+998 (71) 150-15-15', 'tel:+998711501515'),
                          ContactItem('Мобильный', '+998 (90) 176-60-60', 'tel:+998901766060'),
                        ],
                      ),
                      const SizedBox(height: 24),
                      _buildContactCard(
                        context,
                        icon: Icons.email,
                        title: 'Email',
                        items: [
                          ContactItem('Почта', 'business_standart@mail.ru', 'mailto:business_standart@mail.ru'),
                        ],
                      ),
                      const SizedBox(height: 24),
                      _buildContactCard(
                        context,
                        icon: Icons.location_on,
                        title: 'Адрес',
                        items: [
                          ContactItem('Офис', 'г. Ташкент, Узбекистан', null),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const FooterWidget(),
          ],
        ),
      ),
    );
  }

  Widget _buildContactCard(BuildContext context, {
    required IconData icon,
    required String title,
    required List<ContactItem> items,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 16),
                Text(title, style: Theme.of(context).textTheme.titleLarge),
              ],
            ),
            const SizedBox(height: 16),
            ...items.map((item) => _buildContactItem(context, item)),
          ],
        ),
      ),
    );
  }

  Widget _buildContactItem(BuildContext context, ContactItem item) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Text('${item.label}: ', style: Theme.of(context).textTheme.bodyMedium),
          if (item.url != null)
            InkWell(
              onTap: () async {
                final uri = Uri.parse(item.url!);
                if (await canLaunchUrl(uri)) {
                  await launchUrl(uri);
                }
              },
              child: Text(
                item.value,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.primary,
                  decoration: TextDecoration.underline,
                ),
              ),
            )
          else
            Text(item.value, style: Theme.of(context).textTheme.bodyMedium),
        ],
      ),
    );
  }
}

class ContactItem {
  final String label;
  final String value;
  final String? url;

  ContactItem(this.label, this.value, this.url);
}
