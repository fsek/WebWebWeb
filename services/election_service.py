# from api_schemas.candidate_schema import CandidateElectionRead, CandidateRead
# from api_schemas.election_schema import ElectionPostRead, ElectionRead
# from db_models.election_model import Election_DB


# def fix_election_read(election: Election_DB) -> ElectionRead:
#     posts = [
#         ElectionPostRead(
#             id=election_post.post.id,
#             name=election_post.post.name,
#             council_id=election_post.post.council_id,
#         )
#         for election_post in election.election_posts
#     ]

#     print(election.candidates)
#     candidates = [
#         CandidateElectionRead(candidate_id=candidate.candidate_id, user_id=candidate.user_id)
#         for candidate in election.candidates
#     ]

#     electionread = ElectionRead(
#         election_id=election.election_id,
#         title=election.title,
#         start_time=election.start_time,
#         end_time=election.end_time,
#         description=election.description,
#         election_posts=posts,
#         candidates=candidates,
#     )
#     return electionread


# def fix_election_reads(elections: list[Election_DB]) -> list[ElectionRead]:
#     electionreads: list[ElectionRead] = []
#     for election in elections:
#         posts = [
#             ElectionPostRead(
#                 id=election_post.post.id,
#                 name=election_post.post.name,
#                 council_id=election_post.post.council_id,
#             )
#             for election_post in election.election_posts
#         ]

#         electionread = ElectionRead(
#             election_id=election.election_id,
#             title=election.title,
#             start_time=election.start_time,
#             end_time=election.end_time,
#             description=election.description,
#             election_posts=posts,
#             candidates=[],
#         )
#         electionreads.append(electionread)
#     return electionreads
