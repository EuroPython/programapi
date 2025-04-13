from argparse import ArgumentParser

from src.config import Config
from src.utils.parse import Parse
from src.utils.timing_relationships import TimingRelationships
from src.utils.transform import Transform
from src.utils.utils import Utils

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Transform data from Pretalx to EuroPython format and save it."
    )
    parser.add_argument(
        "-w",
        "--warn-dupes",
        action="store_true",
        help="Warn about duplicates in the data.",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        choices=["schedule", "youtube"],
        action="append",
        help="Exclude certain data from transformation.",
    )
    args = parser.parse_args()
    exclude = set(args.exclude or [])

    print(
        f"Parsing submissions from {Config.raw_path}/submissions_latest.json...", end=""
    )
    pretalx_submissions = Parse.publishable_submissions(
        Config.raw_path / "submissions_latest.json"
    )
    print(" done.")

    print(f"\nParsing speakers from {Config.raw_path}/speakers_latest.json...", end="")
    pretalx_speakers = Parse.publishable_speakers(
        Config.raw_path / "speakers_latest.json", pretalx_submissions.keys()
    )
    print(" done.")

    if "youtube" not in exclude:
        print(
            f"Parsing YouTube data from {Config.raw_path}/youtube_latest.json...",
            end="",
        )
        youtube_data = Parse.youtube(Config.raw_path / "youtube_latest.json")
        print(" done.")
    else:
        youtube_data = {}

    print("\nComputing timing relationships...", end="")
    TimingRelationships.compute(pretalx_submissions.values())
    print(" done.")

    print("\nTransforming submissions...", end="")
    ep_sessions = Transform.pretalx_submissions_to_europython_sessions(
        pretalx_submissions,
        youtube_data,
    )
    print(" done.")

    print("\nTransforming speakers...", end="")
    ep_speakers = Transform.pretalx_speakers_to_europython_speakers(pretalx_speakers)
    print(" done.")

    # Warn about duplicates if the flag is set
    if args.warn_dupes:
        Utils.warn_duplicates(
            session_attributes_to_check=["title"],
            speaker_attributes_to_check=["name"],
            sessions_to_check=ep_sessions,
            speakers_to_check=ep_speakers,
        )

    print(f"\nWriting sessions to {Config.public_path}/sessions.json...", end="")
    Utils.write_to_file(Config.public_path / "sessions.json", ep_sessions)
    print(" done.")

    print(f"\nWriting speakers to {Config.public_path}/speakers.json...", end="")
    Utils.write_to_file(Config.public_path / "speakers.json", ep_speakers)
    print(" done.")

    if "schedule" not in exclude:
        print(
            "\nParsing schedule from {Config.raw_path}/schedule_latest.json...", end=""
        )
        pretalx_schedule = Parse.schedule(Config.raw_path / "schedule_latest.json")
        print(" done.")

        print(f"\nTransforming the schedule...", end="")
        ep_schedule = Transform.pretalx_schedule_to_europython_schedule(
            pretalx_schedule.breaks, ep_sessions, ep_speakers
        )
        print(" done.")

        print(f"\nWriting schedule to {Config.public_path}/schedule.json...", end="")
        Utils.write_to_file(
            Config.public_path / "schedule.json", ep_schedule, direct_dump=True
        )
        print(" done.")
