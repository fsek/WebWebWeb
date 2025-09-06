from api_schemas.election_schema import ElectionPopulate
from db_models.election_model import Election_DB
from db_models.post_model import Post_DB
from database import DB_dependency
from fastapi import HTTPException, status
from helpers.types import datetime_utc, ELECTION_ELECTORS, ELECTION_SEMESTERS
from db_models.sub_election_model import SubElection_DB
from db_models.election_post_model import ElectionPost_DB
from typing import List


def service_populate_election(db: DB_dependency, election: Election_DB, data: ElectionPopulate):
    if election.sub_elections:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Election already populated")

    if data.semester not in ("VT", "HT"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid semester")

    # Query all posts
    all_posts = db.query(Post_DB).all()

    # Helper to filter posts for each sub-election
    def filter_posts(semester: ELECTION_SEMESTERS, elector: ELECTION_ELECTORS) -> List[Post_DB]:
        return [post for post in all_posts if post.elected_at_semester == semester and post.elected_by == elector]

    # Guild election
    guild_posts = filter_posts(data.semester, "Guild")
    service_create_sub_election(
        db,
        election,
        f"Council posts elected by the Guild Meeting",
        f"Poster som väljs av sektionsmötet",
        data.end_time_guild,
        guild_posts,
    )

    # Board election
    board_posts = filter_posts(data.semester, "Board")
    service_create_sub_election(
        db,
        election,
        f"Council posts elected by the Board",
        f"Poster som väljs av styrelsen på möte för funktionärsval",
        data.end_time_board,
        board_posts,
    )

    # Board intermediate election
    board_intermediate_posts = filter_posts(data.semester, "Board Intermediate")
    service_create_sub_election(
        db,
        election,
        f"Council posts elected by the Board during the intermediate election board meeting",
        f"Poster som väljs av styrelsen på det mellanliggande valmötet",
        data.end_time_board_intermediate,
        board_intermediate_posts,
    )

    # Educational council election
    educational_council_posts = filter_posts(data.semester, "Educational Council")
    service_create_sub_election(
        db,
        election,
        f"Council posts elected by the Students' Educational Council",
        f"Poster som väljs av studierådet",
        data.end_time_educational_council,
        educational_council_posts,
    )

    db.commit()


def service_create_sub_election(
    db: DB_dependency,
    election: Election_DB,
    title_en: str,
    title_sv: str,
    end_time: datetime_utc,
    eligible_posts: list[Post_DB],
):
    # Handle the posts
    post_ids = set(post.id for post in eligible_posts)

    existing_posts = db.query(Post_DB.id).filter(Post_DB.id.in_(post_ids)).all()
    existing_post_ids = {post.id for post in existing_posts}

    missing_post_ids = post_ids - existing_post_ids
    if missing_post_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Post ids not found: {missing_post_ids}")

    election_posts = [ElectionPost_DB(post_id=post_id) for post_id in post_ids] if post_ids else []

    sub_election = SubElection_DB(
        title_en=title_en,
        title_sv=title_sv,
        end_time=end_time,
        election_id=election.election_id,
        election_posts=election_posts,
    )
    db.add(sub_election)
    db.flush()
    return sub_election
