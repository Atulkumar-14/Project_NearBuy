from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware.metrics import metrics_middleware, get_metrics_summary
from app.db.session import init_db
from app.routers import auth, users, shops, products, reviews, search, admin, uploads, owners, verification, realtime
from jose import jwt, JWTError

app = FastAPI(title="Nearbuy API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await init_db()


# Middleware: secure and log all admin endpoint access attempts
@app.middleware("http")
async def admin_security_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/admin"):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            role = payload.get("role")
            if role != "admin":
                return JSONResponse(status_code=403, content={"detail": "Admin privileges required"})
        except JWTError:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        # Log attempt
        # In real setup, include requester IP, path, and timestamp
        print(f"[ADMIN ACCESS] path={request.url.path}")
    return await call_next(request)


# Middleware: enforce HTTPS for auth endpoints in production-like environments
@app.middleware("http")
async def https_enforcement_middleware(request: Request, call_next):
    if settings.require_https and request.url.path.startswith("/api/auth"):
        # honor proxy header if present
        forwarded_proto = request.headers.get("x-forwarded-proto")
        is_https = request.url.scheme == "https" or (forwarded_proto and forwarded_proto.lower() == "https")
        if not is_https:
            return JSONResponse(status_code=400, content={"detail": "HTTPS is required for authentication."})
    return await call_next(request)

# Middleware: record basic request metrics
app.middleware("http")(metrics_middleware)


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(shops.router, prefix="/api/shops", tags=["shops"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])
app.include_router(owners.router, prefix="/api/owners", tags=["owners"])
app.include_router(verification.router, prefix="/api/verify", tags=["verification"])
app.include_router(realtime.router, prefix="/api/ws", tags=["websocket"])


@app.get("/")
async def read_root():
    return {"message": "Nearbuy API is running"}


@app.get("/api/metrics", tags=["monitoring"])
async def metrics():
    return get_metrics_summary()
