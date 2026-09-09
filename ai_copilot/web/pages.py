"""Server-rendered pages with shareable search and status filters."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ai_copilot.operations.auth import require_session
from ai_copilot.operations.config import WebConfig


def create_pages_router(config: WebConfig) -> APIRouter:
    router = APIRouter(include_in_schema=False)
    templates = Jinja2Templates(directory=Path(__file__).with_name("templates"))
    pages = {page.slug: page for page in config.pages}

    @router.get("/")
    def home(request: Request) -> RedirectResponse:
        require_session(request)
        return RedirectResponse(
            request.url_for("web_page", slug=config.home), status_code=302
        )

    @router.get("/{slug}", response_class=HTMLResponse, name="web_page")
    def page_view(
        request: Request, slug: str, q: str = "", status: str = ""
    ) -> HTMLResponse:
        page = pages.get(slug)
        if page is None:
            return templates.TemplateResponse(
                request=request,
                name="not_found.html",
                context={"config": config, "page": None},
                status_code=404,
            )
        require_session(request)
        query = q.strip().casefold()
        records = [
            record
            for record in page.records
            if (not status or record.status == status)
            and (
                not query
                or query
                in " ".join(
                    [
                        record.key,
                        record.title,
                        record.summary,
                        record.owner,
                        record.detail,
                    ]
                ).casefold()
            )
        ]
        return templates.TemplateResponse(
            request=request,
            name="page.html",
            headers={"Cache-Control": "no-store"},
            context={
                "config": config,
                "page": page,
                "collections": [p for p in config.pages if p.kind == "collection"],
                "records": records,
                "statuses": sorted({record.status for record in page.records}),
                "q": q,
                "status": status,
            },
        )

    return router
