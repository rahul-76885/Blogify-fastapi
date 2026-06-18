from fastapi import Request,HTTPException,status 
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as starlletHTTPException
from blog import app
from blog import templates 
from blog.schemas import PostResponse , PostCreate

posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )

@app.get("/posts/{post_id}",include_in_schema=False)
def post_page(request:Request, post_id:int):
    for post in posts:
        if post.get("id")==post_id:
            title=post["title"][:50]
            return templates.TemplateResponse(
                request,
                "post.html",
                {"title":title,"post":post}
            )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found"  )
   


@app.get("/api/posts",response_model=list[PostResponse])
def get_posts():
    return posts


@app.get("/api/posts/{post_id}",response_model=PostResponse)
def get_post(post_id:int):
    for post in posts:
        if post.get("id")==post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found"  )

@app.post(
    "/api/posts", response_model=PostResponse,status_code=status.HTTP_201_CREATED
)
def create_post(post: PostCreate):
    new_id = max(p["id"] for p in posts) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": "April 23, 2025",
    }
    posts.append(new_post)
    return new_post 

@app.exception_handler(starlletHTTPException)
def general_exception_handler(request:Request,exception:starlletHTTPException):
    if exception.detail :
        message=exception.detail
    else:
        message="An error Occurred"
    
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail":message}
        )
        # jsonresponse is the class 
    
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code
        )
        
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )
        #It returns a list of dictionaries describing every validation error.
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    )
# why we use HttpException instead of returning a dict with status code and message?
# bc using hhtpexception give us more control over the response, and it allows us to raise an exception that can be caught by FastAPI's exception handlers. This way, we can customize the error response and ensure that it follows a consistent format across the application. Additionally, using HTTPException allows us to set specific status codes and messages, making it easier to handle errors in a standardized way.    
