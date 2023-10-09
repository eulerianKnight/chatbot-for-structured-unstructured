# Import Packages
import os


# Utility function for workaround for an existing issue with snowflake
def snowflake_sqlalchemy_20_monkey_patches():
    import sqlalchemy.util.compat

    # make strings always return unicode strings
    sqlalchemy.util.compat.string_types = (str,)
    sqlalchemy.types.String.RETURNS_UNICODE = True

    import snowflake.sqlalchemy.snowdialect

    snowflake.sqlalchemy.snowdialect.SnowflakeDialect.returns_unicode_strings = True

    # make has_table() support the `info_cache` kwarg
    import snowflake.sqlalchemy.snowdialect

    def has_table(self, connection, table_name, schema=None, info_cache=None):
        """
        Checks if the table exists
        """
        return self._has_object(connection, "TABLE", table_name, schema)

    snowflake.sqlalchemy.snowdialect.SnowflakeDialect.has_table = has_table


# def describeSnowparkDF(snowpark_df: snowpark.DataFrame):
#     """
#     Function to describe table loaded in Snowpark DataFrame format
#     :param snowpark_df:
#     :return:
#     """
#     st.write("Here is some statistics about the loaded data:")
#     numeric_types = [T.DecimalType, T.LongType, T.DoubleType, T.FloatType, T.IntegerType]
#     numeric_columns = [c.name for c in snowpark_df.schema.fields if type(c.datatype) in numeric_types]
#
#     # Get Categorical Columns
#     categorical_types = [T.StringType]
#     categorical_columns = [c.name for c in snowpark_df.schema.fields if type(c.datatype) in categorical_types]
#
#     st.write("Relational Schema:")
#
#     columns = [c for c in snowpark_df.schema.fields]
#     st.write(columns)
#
#     col1, col2 = st.columns(2)
#     with col1:
#         st.write(f"Numeric Columns:\t{numeric_columns}")
#     with col2:
#         st.write(f"Categorical columns:\t{categorical_columns}")
#
#     # Calculate Statistics for our dataset
#     st.dataframe(snowpark_df.describe().sort('SUMMARY STATISTICS'), use_container_width=True)


# File path for storing the variables for pfizer_index_id and merck_index_id
variable_file = "variables.txt"


def load_variables():
    global pfizer_index_id, merck_index_id
    # Check if Variables file exists
    if os.path.isfile(variable_file):
        with open(variable_file, "r") as file:
            # Read Values from the file
            values = file.read().split(",")
            pfizer_index_id = values[0]
            merck_index_id = values[0]


def save_variables(pfizer_index_id, merck_index_id):
    # Write Values to file
    with open(variable_file, "w") as file:
        file.write(f"{pfizer_index_id}, {merck_index_id}")
