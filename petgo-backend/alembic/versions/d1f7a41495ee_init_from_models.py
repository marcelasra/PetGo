"""init from models (PetGo) — users, ngos, reports, photos, moderation, trust, geofence"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2.types import Geography, Geometry

# Alembic identifiers
revision = "d1f7a41495ee"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 0) PostGIS
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # 1) ENUMs idempotentes (garante que existem e evita DuplicateObject)
    op.execute("""
    DO $$
    BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reportstatus') THEN
        CREATE TYPE reportstatus AS ENUM ('REPORTADO','EM_ATENDIMENTO','RESOLVIDO','UNDER_REVIEW','REJECTED','PUBLISHED');
      END IF;
    END$$;
    """)
    op.execute("""
    DO $$
    BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'visibility') THEN
        CREATE TYPE visibility AS ENUM ('PUBLIC','FOGGED','ONG_ONLY');
      END IF;
    END$$;
    """)
    op.execute("""
    DO $$
    BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'role') THEN
        CREATE TYPE role AS ENUM ('USER','ONG','ADMIN');
      END IF;
    END$$;
    """)
    op.execute("""
    DO $$
    BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'moderationdecision') THEN
        CREATE TYPE moderationdecision AS ENUM ('APPROVED','REJECTED','MANUAL_REVIEW');
      END IF;
    END$$;
    """)
    op.execute("""
    DO $$
    BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contentflagstatus') THEN
        CREATE TYPE contentflagstatus AS ENUM ('OPEN','UNDER_REVIEW','CLOSED');
      END IF;
    END$$;
    """)

    # 2) Tabelas base (usando os ENUMs existentes, sem recriar)
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(120), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("USER", "ONG", "ADMIN", name="role", create_type=False),
            nullable=False,
            server_default="USER",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )

    op.create_table(
        "ngos",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("radius_km", sa.String(10), server_default="3.0"),
        sa.Column("phone", sa.String(40)),
        sa.Column("description", sa.Text()),
    )

    op.create_table(
        "reports",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),

        sa.Column(
            "status",
            sa.Enum(
                "REPORTADO", "EM_ATENDIMENTO", "RESOLVIDO", "UNDER_REVIEW", "REJECTED", "PUBLISHED",
                name="reportstatus",
                create_type=False,
            ),
            nullable=False,
            server_default="UNDER_REVIEW",
        ),
        sa.Column(
            "visibility_level",
            sa.Enum("PUBLIC", "FOGGED", "ONG_ONLY", name="visibility", create_type=False),
            nullable=False,
            server_default="PUBLIC",
        ),

        sa.Column("geom", Geography(geometry_type="POINT", srid=4326), nullable=False),
        sa.Column("approx_geom", Geometry(geometry_type="POINT", srid=4326), nullable=True),

        sa.Column("address_text", sa.String(200)),
        sa.Column("description", sa.String(500)),
        sa.Column("animal_type", sa.String(20), server_default="DESCONHECIDO"),

        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )

    op.create_table(
        "report_photos",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("report_id", sa.BigInteger(), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )

    op.create_table(
        "moderation_events",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("report_id", sa.BigInteger(), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(40)),
        sa.Column("score", sa.String(40)),
        sa.Column(
            "decision",
            sa.Enum("APPROVED", "REJECTED", "MANUAL_REVIEW", name="moderationdecision", create_type=False),
            nullable=False,
        ),
        sa.Column("reviewer_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )

    op.create_table(
        "content_flags",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("report_id", sa.BigInteger(), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reporter_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("reason", sa.String(120), nullable=False),
        sa.Column(
            "status",
            sa.Enum("OPEN", "UNDER_REVIEW", "CLOSED", name="contentflagstatus", create_type=False),
            nullable=False,
            server_default="OPEN",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )

    op.create_table(
        "trust_signals",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )

    op.create_table(
        "geofence_zones",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("rule", sa.String(40), nullable=False, server_default="ONG_ONLY"),
        sa.Column("geom", Geometry(geometry_type="POLYGON", srid=4326), nullable=False),
    )

    # 3) Índices GIST
    op.execute("CREATE INDEX IF NOT EXISTS idx_reports_geom ON reports USING GIST (geom);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_reports_approx_geom ON reports USING GIST (approx_geom);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_geofence_geom ON geofence_zones USING GIST (geom);")

    # 4) approx_geom ~110m (grid 0.001 grau)
    op.execute("""
    CREATE OR REPLACE FUNCTION set_approx_geom()
    RETURNS trigger AS $$
    BEGIN
      NEW.approx_geom := ST_SnapToGrid(NEW.geom::geometry, 0.001);
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_reports_set_approx_geom'
      ) THEN
        CREATE TRIGGER trg_reports_set_approx_geom
        BEFORE INSERT OR UPDATE OF geom ON reports
        FOR EACH ROW EXECUTE PROCEDURE set_approx_geom();
      END IF;
    END$$;
    """)


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS trg_reports_set_approx_geom ON reports;")
    op.execute("DROP FUNCTION IF EXISTS set_approx_geom();")

    op.execute("DROP INDEX IF EXISTS idx_reports_approx_geom;")
    op.execute("DROP INDEX IF EXISTS idx_reports_geom;")
    op.execute("DROP INDEX IF EXISTS idx_geofence_geom;")

    op.drop_table("geofence_zones")
    op.drop_table("trust_signals")
    op.drop_table("content_flags")
    op.drop_table("moderation_events")
    op.drop_table("report_photos")
    op.drop_table("reports")
    op.drop_table("ngos")
    op.drop_table("users")

    # Enums
    op.execute("DROP TYPE IF EXISTS contentflagstatus;")
    op.execute("DROP TYPE IF EXISTS moderationdecision;")
    op.execute("DROP TYPE IF EXISTS role;")
    op.execute("DROP TYPE IF EXISTS visibility;")
    op.execute("DROP TYPE IF EXISTS reportstatus;")
