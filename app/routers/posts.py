from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_303_SEE_OTHER
from app.database import get_db
from app.models.models import Post
from fastapi.templating import Jinja2Templates
import os
import logging

# Directory for uploads
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/post", response_class=HTMLResponse)
async def display_posts(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return templates.TemplateResponse("post.html", {"request": request, "posts": posts})

@router.get("/posts", response_class=HTMLResponse)
async def posts(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        return RedirectResponse(url="/login")  # Redirect if not logged in
    
    # Fetch user posts
    posts = db.query(Post).filter(Post.user_id == user_id).all()
    return templates.TemplateResponse("user_post.html", {"request": request, "posts": posts})


@router.get("/create_post", response_class=HTMLResponse)
async def create_post(request: Request):
    user_id = request.session.get('user_id')
    if not user_id:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("create_post.html", {"request": request, "user_id": user_id})


@router.get("/posts/{post_id}", response_class=HTMLResponse)
async def view_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("view_post.html", {"request": request, "post": post})

@router.get("/posts/{post_id}/delete", response_class=HTMLResponse)
async def delete_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post)
    db.commit()
    
    return RedirectResponse(url="/dashboard/#posts", status_code=HTTP_303_SEE_OTHER)



@router.get("/posts/{post_id}/edit", response_class=HTMLResponse)
async def edit_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post})






logger = logging.getLogger(__name__)



@router.get("/create_post")
async def create_post(request: Request, db: Session = Depends(get_db)):
    new_post = None  # Optional: replace with logic to fetch a new post if needed
    media_url = None  # Define media_url as None for the GET request
    return templates.TemplateResponse("create_post.html", {"request": request, "new_post": new_post, "media_url": media_url})



@router.post("/create_post", response_class=HTMLResponse)
async def create_post_post(
    request: Request,
    # id: int = Form(...),  # Accept `id` as a form field
    title: str = Form(...), 
    subtitle: str = Form(...), 
    description: str = Form(...), 
    media: UploadFile = File(None),  # Accept media (image or video)
    db: Session = Depends(get_db)
):
    # Check user session
    user_id = request.session.get('user_id')
    if not user_id:
        return RedirectResponse(url="/login")

    # Initialize variables
    media_url = None
    error_message = None

    # Validate file type and size if media is provided
    if media:
        # Extract file extension
        file_extension = media.filename.split('.')[-1].lower()
        # Define supported file types and max size (in bytes)
        valid_extensions = {"mp4", "avi", "mov", "mkv", "jpg", "jpeg", "png", "gif"}
        max_file_size = 5 * 1024 * 1024  # 5MB limit

        if file_extension not in valid_extensions:
            error_message = "Unsupported file type. Allowed types: png, gif, mov, avi."
        elif len(await media.read()) > max_file_size:
            error_message = "File is too large. Maximum allowed size is 5MB."
        else:
            # Proceed with saving the file
            upload_dir = "uploads/media"
            os.makedirs(upload_dir, exist_ok=True)
            # file_path = os.path.join(upload_dir, media.filename)
            
            # Sanitize filename and save #désinfectefer it means to replace espaces with underscores
            sanitized_filename = media.filename.replace(" ", "_")
            sanitized_path = os.path.join(upload_dir, sanitized_filename)
            with open(sanitized_path, "wb") as f:
                f.write(await media.read())
            
            media_url = f"/static/media/{sanitized_filename}"

    # Show error if file validation fails
    if error_message:
        return templates.TemplateResponse(
            "create_post.html",
            {"request": request, "error_message": error_message}
        )

    try:
        # Create and save the new post
        new_post = Post(
            title=title, 
            subtitle=subtitle, 
            description=description, 
            user_id=user_id, 
            media_url=media_url
        )
        db.add(new_post)
        db.commit()

    except Exception as e:
        # Handle database errors
        db.rollback()
        return templates.TemplateResponse(
            "create_post.html", 
            {"request": request, "error_message": "Error creating post. Please try again later."}
        )

    return RedirectResponse(url="/dashboard/?success=true", status_code=303)




@router.post("/posts/{post_id}/edit", response_class=HTMLResponse)
async def update_post(
    request: Request,
    post_id: int,
    title: str = Form(...),
    subtitle: str = Form(...),
    description: str = Form(...),
    media: UploadFile = File(None),  # Accepting media file
    db: Session = Depends(get_db)
):
    logger.info("Starting to update post")
    
    # Get the post by id
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Update the post with the new data
    post.title = title
    post.subtitle = subtitle
    post.description = description
    
    # Handle media file if provided
    if media:
        logger.info(f"Media file received: {media.filename}")
        media_path = f"static/media/{media.filename}"
        
        # Save the media file
        with open(media_path, "wb") as f:
            f.write(await media.read())
        
        # Update the media_url in the post
        post.media_url = f"/static/media/{media.filename}"
        logger.info(f"Media URL updated: {post.media_url}")

    # Commit the changes to the database
    db.commit()
    logger.info("Post updated successfully")
    
    # Redirect to the dashboard with a success message
    return RedirectResponse(url=f"/dashboard/?success=true&highlighted={post_id}", status_code=303)





