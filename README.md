# Grocery Graph — Django + DRF + Neo4j

End-to-end starter implementing your spec with best practices.

## Run (Docker)
```bash
git clone https://github.com/trixtipsfix/groc-store-api.git
cd groc-store-api
cp .env.example .env
sudo docker compose up -d --build
```
Create an admin user and promote to ADMIN:
```bash
sudo docker compose exec web python manage.py createsuperuser
sudo docker compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model as g; U=g(); u=U.objects.get(is_superuser=True); u.role='ADMIN'; u.save(); print('Promoted to ADMIN')"
```
## Live Link
```
https://infocentree.com
```

## JWT Auth
- `/api/auth/token/` and `/api/auth/token/refresh/`

## Docs
- Swagger: `/api/schema/swagger/`
- Redoc: `/api/schema/redoc/`
