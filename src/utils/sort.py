class Sort:
    @staticmethod
    def sort_nested(data, sort_keys=None):
        """
        TODO: This is probably too generic and not the best way, but it works for now
        """
        if sort_keys is None:
            sort_keys = ["start", "code", "title", "name"]

        def get_sort_key(item):
            return tuple(item.get(key, "") for key in sort_keys)

        if isinstance(data, dict):
            return {
                key: Sort.sort_nested(value, sort_keys)
                for key, value in sorted(data.items())
            }
        elif isinstance(data, list):
            if all(isinstance(item, dict) for item in data):
                return sorted(
                    (Sort.sort_nested(item, sort_keys) for item in data),
                    key=get_sort_key,
                )
            else:
                return sorted(Sort.sort_nested(item, sort_keys) for item in data)
        else:
            return data
