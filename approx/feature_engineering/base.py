class FeatureModule:
    def __init__(self, approx, ptable):
        self.approx = approx
        self.ptable = ptable
        self._shared_cache = approx.__dict__.setdefault(
            "_feature_engineering_cache",
            {
                "balance": {},
                "parsed": {},
                "rows": {},
                "configs": {},
            },
        )

    def parse_result(self, result):
        all_elems = []
        var_elems = []
        for st in result.oxidation_states:
            all_elems.append((st.element, st.oxidation_state, st.quantity))
            if not st.is_fixed:
                var_elems.append((st.element, st.oxidation_state, st.quantity))
        return all_elems, var_elems

    def get_balance_result(self, formula):
        balance_cache = self._shared_cache["balance"]
        if formula not in balance_cache:
            balance_cache[formula] = self.approx.charge_balance(formula)
        return balance_cache[formula]

    def get_parsed_elements(self, formula):
        parsed_cache = self._shared_cache["parsed"]
        if formula not in parsed_cache:
            parsed_cache[formula] = self.parse_result(self.get_balance_result(formula))
        return parsed_cache[formula]

    def get_element_row(self, element):
        row_cache = self._shared_cache["rows"]
        if not row_cache:
            for _, row in self.ptable.iterrows():
                row_cache[row["symbol"]] = row
        return row_cache[element]

    def get_electronic_configuration(self, element):
        config_cache = self._shared_cache["configs"]
        if element not in config_cache:
            row = self.get_element_row(element)
            from mendeleev.econf import ElectronicConfiguration

            config_cache[element] = ElectronicConfiguration(
                row["electronic_configuration"]
            )
        return config_cache[element]

    @staticmethod
    def zero_fill_from_all(all_features):
        return {key.replace("all_", "var_"): 0.0 for key in all_features}

    def filter_mode(self, features, mode):
        if mode == "both":
            return features
        if mode == "all":
            return {k: v for k, v in features.items() if k.startswith("all_")}
        if mode == "var":
            return {k: v for k, v in features.items() if k.startswith("var_")}
        raise ValueError("mode must be: all, var, both")

    def get_features(self, formula):
        raise NotImplementedError