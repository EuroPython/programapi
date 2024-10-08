import sys

from src.config import Config
from src.utils.parse import Parse
from src.utils.timing_relationships import TimingRelationships
from src.utils.transform import Transform
from src.utils.utils import Utils

if __name__ == "__main__":
    print(f"Parsing the data from {Config.raw_path}...")
    pretalx_submissions = Parse.publishable_submissions(
        Config.raw_path / "submissions_latest.json"
    )
    pretalx_speakers = Parse.publishable_speakers(
        Config.raw_path / "speakers_latest.json", pretalx_submissions.keys()
    )
    pretalx_schedule = Parse.schedule(Config.raw_path / "schedule_latest.json")

    # Parse the YouTube data
    youtube_data = Parse.youtube(Config.raw_path / "youtube_latest.json")

    print("Computing timing relationships...")
    TimingRelationships.compute(pretalx_submissions.values())

    print("Transforming the data...")
    ep_sessions = Transform.pretalx_submissions_to_europython_sessions(
        pretalx_submissions,
        youtube_data,
    )
    ep_speakers = Transform.pretalx_speakers_to_europython_speakers(pretalx_speakers)
    ep_schedule = Transform.pretalx_schedule_to_europython_schedule(
        pretalx_schedule.breaks, ep_sessions, ep_speakers
    )

    # Warn about duplicates if the flag is set
    if len(sys.argv) > 1 and sys.argv[1] == "--warn-dupes":
        Utils.warn_duplicates(
            session_attributes_to_check=["title"],
            speaker_attributes_to_check=["name"],
            sessions_to_check=ep_sessions,
            speakers_to_check=ep_speakers,
        )

    print(f"Writing the data to {Config.public_path}...")
    Utils.write_to_file(Config.public_path / "sessions.json", ep_sessions)
    Utils.write_to_file(Config.public_path / "speakers.json", ep_speakers)
    Utils.write_to_file(
        Config.public_path / "schedule.json", ep_schedule, direct_dump=True
    )
