from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.socialfeed.routes import router as socialfeed_router
from app.prompts.routes import router as prompts_router
from app.leaderboard.routes import router as leaderboard_router
from app.marketplace.routes import router as marketplace_router
from app.encrypt.routes import router as encrypt_router



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """
    Redirects users from the root endpoint to the docs endpoint.
    """
    return RedirectResponse(url="/docs")


@app.get("/health")
def read_root():
    return {"Hello": "Service is live"}


app.include_router(socialfeed_router, prefix="/socialfeed")
app.include_router(prompts_router, prefix="/prompts")
app.include_router(leaderboard_router, prefix="/leaderboard")
app.include_router(marketplace_router, prefix="/marketplace")
# app.include_router(encrypt_router, prefix="/encrypt")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)