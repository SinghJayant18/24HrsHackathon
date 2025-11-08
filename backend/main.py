from fastapi import FastAPI, Response
import httpx
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .settings import settings
from .routers_items import router as items_router
from .routers_orders import router as orders_router
from .routers_reports import router as reports_router
from .routers_tracking import router as tracking_router
from .routers_catalogue import router as catalogue_router
from .routers_taxes import router as taxes_router
from .routers_auth import router as auth_router
from .migrations import migrate_add_expected_delivery_date


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)
    # Run migrations
    migrate_add_expected_delivery_date()
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(items_router)
    app.include_router(orders_router)
    app.include_router(reports_router)
    app.include_router(tracking_router)
    app.include_router(catalogue_router)
    app.include_router(taxes_router)

    @app.get("/")
    def root():
        return {"ok": True, "service": settings.app_name}

    # Prevent browser 404 requests for favicon
    @app.get("/favicon.ico")
    async def favicon():
        if not settings.favicon_url:
            return Response(status_code=204)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(settings.favicon_url)
            if resp.status_code != 200 or not resp.content:
                return Response(status_code=204)
            media_type = resp.headers.get("content-type", "image/x-icon")
            return Response(content=resp.content, media_type=media_type)
        except Exception:
            return Response(status_code=204)

    return app


app = create_app()
