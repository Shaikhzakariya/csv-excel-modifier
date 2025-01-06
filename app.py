import pandas as pd
import os
import json
import streamlit as st

class CSVExcelModifier:
    def __init__(self):
        self.log = []  # To record progress of modifications

    def log_action(self, action):
        self.log.append(action)

    def remove_duplicates(self, df):
        initial_count = len(df)
        df_cleaned = df.drop_duplicates()
        final_count = len(df_cleaned)

        self.log_action({
            "action": "remove_duplicates",
            "details": f"Removed {initial_count - final_count} duplicate rows."
        })

        return df_cleaned

    def apply_rules(self, df, rules):
        try:
            for rule in rules:
                column, condition, value = rule["column"], rule["condition"], rule["value"]
                if condition == "greater_than":
                    df = df[df[column] > value]
                elif condition == "less_than":
                    df = df[df[column] < value]
                elif condition == "equals":
                    df = df[df[column] == value]

            self.log_action({
                "action": "apply_rules",
                "details": f"Applied rules: {rules}. Remaining rows: {len(df)}"
            })

            return df
        except Exception as e:
            st.error(f"Error applying rules: {e}")
            return df

    def add_or_delete_rows(self, df, operations):
        try:
            for operation in operations:
                action, row_data = operation["action"], operation.get("row_data")
                if action == "add":
                    df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
                elif action == "delete":
                    index_to_delete = operation.get("index")
                    if index_to_delete is not None and 0 <= index_to_delete < len(df):
                        df = df.drop(index_to_delete)

            self.log_action({
                "action": "add_or_delete_rows",
                "details": f"Performed operations: {operations}. Final rows: {len(df)}"
            })

            return df
        except Exception as e:
            st.error(f"Error performing operations: {e}")
            return df

    def save_log(self):
        return self.log

# Streamlit UI
def main():
    st.title("CSV/Excel Modifier Tool")
    st.write("Welcome to the CSV/Excel Modifier! Upload your file and choose an operation.")

    modifier = CSVExcelModifier()

    uploaded_file = st.file_uploader("Upload a CSV/Excel file", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.write("### Uploaded File:", df)

            operation = st.selectbox("Choose an operation", ["Remove Duplicates", "Apply Rules", "Add/Delete Rows"])

            if operation == "Remove Duplicates":
                if st.button("Run Operation"):
                    df = modifier.remove_duplicates(df)
                    st.write("### Modified File:", df)

            elif operation == "Apply Rules":
                rules_input = st.text_area("Enter rules in JSON format (e.g., [{\"column\": \"Column1\", \"condition\": \"greater_than\", \"value\": 10}])")
                if st.button("Run Operation"):
                    try:
                        rules = json.loads(rules_input)
                        df = modifier.apply_rules(df, rules)
                        st.write("### Modified File:", df)
                    except Exception as e:
                        st.error(f"Error parsing rules: {e}")

            elif operation == "Add/Delete Rows":
                operations_input = st.text_area("Enter operations in JSON format (e.g., [{\"action\": \"add\", \"row_data\": {\"Column1\": 30, \"Column2\": \"F\", \"Column3\": 600}}, {\"action\": \"delete\", \"index\": 0}])")
                if st.button("Run Operation"):
                    try:
                        operations = json.loads(operations_input)
                        df = modifier.add_or_delete_rows(df, operations)
                        st.write("### Modified File:", df)
                    except Exception as e:
                        st.error(f"Error parsing operations: {e}")

            if st.button("Download Modified File"):
                output_file = "modified_file.csv"
                df.to_csv(output_file, index=False)
                st.download_button("Download", data=df.to_csv(index=False), file_name=output_file, mime="text/csv")

            st.write("### Modification Log:", modifier.save_log())
        except Exception as e:
            st.error(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
