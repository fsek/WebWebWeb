from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from db_models.permission_model import Permission_DB
from db_models.post_model import Post_DB


# unassign a permission on a post
def unassign_permission(post: Post_DB, permission_id: int, db: Session):
    delete_count = 0
    for existing_perm in post.permissions:
        if existing_perm.id == permission_id:
            post.permissions.remove(existing_perm)
            db.commit()
            delete_count += 1
            # let the loop continue just incase somehow there's duplicates

    if delete_count == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Permission not found on post")


# assign an existing permission to given post
def assign_permission(post: Post_DB, permission_id: int, db: Session):
    perm_to_assign = db.query(Permission_DB).filter(Permission_DB.id == permission_id).one_or_none()

    if perm_to_assign is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Permission to assign was not found")

    for perm in post.permissions:
        if perm.id == perm_to_assign.id:
            # post already has this permission
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Permission already assigned")

    post.permissions.append(perm_to_assign)
    db.commit()
