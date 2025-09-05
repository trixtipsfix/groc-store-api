# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from neomodel import db
from neo4j.exceptions import ServiceUnavailable

User = get_user_model()

@receiver(post_save, sender=User)
def sync_user_to_graph(sender, instance, created, **kwargs):
    params = {
        "user_id": str(instance.id),
        "name": instance.name,
        "email": instance.email,
        "role": instance.role,
    }
    try:
        db.cypher_query(
            """
            // Ensure both labels to match neomodel class resolution
            MERGE (u:UserNode:BaseNode {user_id: $user_id})
            ON CREATE SET
                u.uid = coalesce(u.uid, replace(toString(randomUUID()), '-', '')),
                u.created_at = timestamp()/1000.0
            SET
                u.name = $name,
                u.email = $email,
                u.role = $role,
                u.updated_at = timestamp()/1000.0
            """,
            params,
        )
    except ServiceUnavailable as e:
        import logging
        logging.getLogger(__name__).warning("Neo4j unavailable during user sync: %s", e)
