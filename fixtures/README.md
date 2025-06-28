# Database Fixtures

## Loading Initial Data

To load the initial database fixtures:

```bash
python manage.py loaddata fixtures/initial_data.json
```

## Creating New Fixtures

To create new fixtures from current database:

```bash
python manage.py dumpdata tenants integrations mock_services --indent 2 > fixtures/initial_data.json
```

## What's Included

- Default tenant (domain: 'default')
- Admin user (username: 'admin', password: 'admin123')
- External services (user-service, payment-service, communication-service)
- Sample webhook endpoints and configurations