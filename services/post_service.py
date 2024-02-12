from api_schemas.post_schemas import PostCreate
from sqlalchemy.orm import Session
from db_models.post_model import Post_DB


def create_new_post(data: PostCreate, db: Session):
    post = Post_DB(name=data.name, council_id=data.council_id)
    db.add(post)
    db.commit()
    return post
