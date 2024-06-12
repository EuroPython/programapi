class Sort:
    @staticmethod
    def sort_nested(data):
        """
        TODO: This is probably too generic and not the best way, but it works for now
        """
        if isinstance(data, dict):
            return {key: Sort.sort_nested(value) for key, value in sorted(data.items())}
        elif isinstance(data, list):
            if all(isinstance(item, dict) for item in data):
                # Sort by start time in schedule
                return sorted(
                    (Sort.sort_nested(item) for item in data),
                    key=lambda x: x.get("start", ""),
                )
            else:
                return sorted(Sort.sort_nested(item) for item in data)
        else:
            return data
