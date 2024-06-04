import json
from collections.abc import KeysView
from pathlib import Path

from slugify import slugify

from src.models.europython import EuroPythonSession, EuroPythonSpeaker
from src.models.pretalx import PretalxSpeaker, PretalxSubmission


class Utils:
    @staticmethod
    def publishable_sessions_of_speaker(
        speaker: PretalxSpeaker, accepted_proposals: KeysView[str]
    ) -> set[str]:
        return set(speaker.submissions) & accepted_proposals

    @staticmethod
    def find_duplicate_attributes(
        objects: (
            dict[str, EuroPythonSession]
            | dict[str, EuroPythonSpeaker]
            | dict[str, PretalxSubmission]
            | dict[str, PretalxSpeaker]
        ),
        attributes: list[str],
    ) -> dict[str, list[str]]:
        """
        Find duplicates in the given objects based on the given attributes

        Returns: dict[attribute_value, list[object_code]]
        """
        duplicates: dict[str, list[str]] = {}
        for obj in objects.values():
            for attribute in attributes:
                value = getattr(obj, attribute)
                if value in duplicates:
                    duplicates[value].append(obj.code)
                else:
                    duplicates[value] = [obj.code]

        return duplicates

    @staticmethod
    def replace_duplicate_slugs(code_to_slug: dict[str, str]) -> dict[str, str]:
        slug_count: dict[str, int] = {}
        seen_slugs: set[str] = set()

        for code, slug in code_to_slug.items():
            original_slug = slug

            if original_slug in seen_slugs:
                if original_slug in slug_count:
                    slug_count[original_slug] += 1
                else:
                    slug_count[original_slug] = 1
                code_to_slug[code] = f"{original_slug}-{slug_count[original_slug]}"
            else:
                seen_slugs.add(original_slug)

        return code_to_slug

    @staticmethod
    def warn_duplicates(
        session_attributes_to_check: list[str],
        speaker_attributes_to_check: list[str],
        sessions_to_check: dict[str, EuroPythonSession] | dict[str, PretalxSubmission],
        speakers_to_check: dict[str, EuroPythonSpeaker] | dict[str, PretalxSpeaker],
    ) -> None:
        """
        Warns about duplicate attributes in the given objects
        """
        print(
            f"Checking for duplicate {'s, '.join(session_attributes_to_check)}s in sessions..."
        )
        duplicate_sessions = Utils.find_duplicate_attributes(
            sessions_to_check, session_attributes_to_check
        )

        for attribute, codes in duplicate_sessions.items():
            if len(codes) > 1:
                print(f"Duplicate ``{attribute}`` in sessions: {codes}")

        print(
            f"Checking for duplicate {'s, '.join(speaker_attributes_to_check)}s in speakers..."
        )
        duplicate_speakers = Utils.find_duplicate_attributes(
            speakers_to_check, speaker_attributes_to_check
        )

        for attribute, codes in duplicate_speakers.items():
            if len(codes) > 1:
                print(f"Duplicate ``{attribute}`` in speakers: {codes}")

    @staticmethod
    def compute_unique_slugs_by_attribute(
        objects: dict[str, PretalxSubmission] | dict[str, PretalxSpeaker],
        attribute: str,
    ) -> dict[str, str]:
        """
        Compute the slugs based on the given attribute
        and replace the duplicate slugs with incrementing
        numbers at the end.

        Returns: dict[code, slug]
        """
        object_code_to_slug = {}
        for obj in objects.values():
            object_code_to_slug[obj.code] = slugify(getattr(obj, attribute))

        return Utils.replace_duplicate_slugs(object_code_to_slug)

    @staticmethod
    def write_to_file(
        output_file: Path | str,
        data: dict[str, EuroPythonSession] | dict[str, EuroPythonSpeaker],
    ) -> None:
        with open(output_file, "w") as fd:
            json.dump(
                {k: json.loads(v.model_dump_json()) for k, v in data.items()},
                fd,
                indent=2,
            )
