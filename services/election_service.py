from api_schemas.election_schema import ElectionPostRead, ElectionRead
from db_models.election_model import Election_DB


def fix_election_read(election: Election_DB) -> ElectionRead:
    posts = [ElectionPostRead(id=post.id, name=post.name, council_id=post.council_id) for post in election.posts]

    electionread = ElectionRead(
        election_id=election.election_id,
        title=election.title,
        start_time=election.start_time,
        end_time=election.end_time,
        description=election.description,
        election_posts=posts,
        candidates=[],
    )
    return electionread


def fix_election_reads(elections: list[Election_DB]) -> list[ElectionRead]:
    electionreads: list[ElectionRead] = []
    for election in elections:
        posts = [ElectionPostRead(id=post.id, name=post.name, council_id=post.council_id) for post in election.posts]

        electionread = ElectionRead(
            election_id=election.election_id,
            title=election.title,
            start_time=election.start_time,
            end_time=election.end_time,
            description=election.description,
            election_posts=posts,
            candidates=[],
        )
        electionreads.append(electionread)
    return electionreads
