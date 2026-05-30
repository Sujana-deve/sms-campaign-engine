from django.apps import AppConfig
import os
import sys


class CampaignsConfig(AppConfig):
    name = 'campaigns'

    def ready(self):
        # Add project root to path so db module is findable
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from db.connection import get_connection
        try:
            conn = get_connection()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE campaigns SET status = 'failed' WHERE status = 'running'"
            )
            updated = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            if updated > 0:
                print(f"[Startup] Reset {updated} orphaned campaign(s) from 'running' to 'failed'.")
        except Exception as e:
            print(f"[Startup] Could not reset orphaned campaigns: {e}")