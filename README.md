# Grocery Graph — Django + DRF + Neo4j

A full-stack starter implementing groceries, suppliers, incomes, and items using Django REST Framework + Neo4j.

---

## Quick Start (Docker)

```bash
git clone https://github.com/trixtipsfix/groc-store-api.git
cd groc-store-api
cp .env.example .env

# start services
sudo docker compose up -d --build

# create superuser
sudo docker compose exec web python manage.py createsuperuser

# promote to ADMIN
sudo docker compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model as g;
U = g(); u = U.objects.get(is_superuser=True);
u.role='ADMIN'; u.save();
print('Promoted to ADMIN')
"
```

App will be available at:

```
http://localhost:80
```
You can access the live API link at:

```
https://infocentree.com
```
Want to see it in action? 

Visit this live website:

```
https://grocery-store-frontend-ten.vercel.app/

username: admin
password: password123
```
---

## Authentication (JWT)

- `POST /api/auth/token/` — get access/refresh token  
- `POST /api/auth/token/refresh/` — refresh access token  

All subsequent requests require `Authorization: Bearer <token>`.

---

## Endpoints

### Users
- `GET /api/users/` — list all users (ADMIN only)  
- `POST /api/users/` — create supplier or staff  
- `GET /api/users/{id}/` — retrieve a user  
- `PATCH /api/users/{id}/` — update a user  
- `DELETE /api/users/{id}/` — delete a user  

### Groceries
- `GET /api/groceries/` — list groceries  
- `POST /api/groceries/` — create grocery (ADMIN only)  
- `GET /api/groceries/{uid}/` — retrieve grocery  
- `PATCH /api/groceries/{uid}/` — update grocery (responsible supplier or ADMIN)  
- `DELETE /api/groceries/{uid}/` — delete grocery (ADMIN only)  

### Items
- `GET /api/groceries/{grocery_uid}/items/` — list grocery’s items  
- `POST /api/groceries/{grocery_uid}/items/` — create item (responsible supplier or ADMIN)  
- `PATCH /api/items/{uid}/` — update item  
- `DELETE /api/items/{uid}/` — delete item  

### Daily Incomes
- `GET /api/groceries/{grocery_uid}/incomes/` — list incomes  
  - supports `?mine=1` (only incomes for groceries where you are responsible)  
- `POST /api/groceries/{grocery_uid}/incomes/` — record new income  
- `PATCH /api/incomes/{uid}/` — update income  
- `DELETE /api/incomes/{uid}/` — delete income  

---

## API Docs

- Swagger UI → `/api/schema/swagger/`  
- Redoc → `/api/schema/redoc/`  

---

## Notes
- Data is persisted in **Neo4j** (graph database).  
- Relationships:
  - `(Supplier)-[:RESPONSIBLE_FOR]->(Grocery)`
  - `(Grocery)-[:HAS_ITEM]->(Item)`
  - `(Grocery)-[:HAS_INCOME]->(DailyIncome)`  
- Enforced roles: `ADMIN`, `SUPPLIER`, `STAFF`.  

---

## Smoke Test

Quick end-to-end check:

```bash
python smoke_test.py --base http://localhost:80 \
  --admin-username admin --admin-password password123
```

---
