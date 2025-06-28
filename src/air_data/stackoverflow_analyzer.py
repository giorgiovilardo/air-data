from pathlib import Path

import duckdb
import pandas as pd


class StackOverflowAnalyzer:
    def __init__(self) -> None:
        # Initialize in-memory DuckDB connection
        self.conn: duckdb.DuckDBPyConnection = duckdb.connect(":memory:")

        # Get paths to CSV files relative to this module
        base_path = Path(__file__).parent / "so_data"
        self.data_csv_path: Path = (
            base_path / "so_2024_sample.csv"
        )  # Updated to use sample file
        self.schema_csv_path: Path = base_path / "so_2024_raw_schema.csv"

        # Read CSV files into DuckDB tables and create star schema
        self._load_data()
        self._create_star_schema()

    def _load_data(self) -> None:
        """Load CSV files into DuckDB tables using native CSV reading facilities."""
        # Load the main data CSV
        self.conn.execute(f"""
            CREATE TABLE survey_data AS
            SELECT * FROM read_csv_auto('{self.data_csv_path}')
        """)

        # Load the schema CSV
        self.conn.execute(f"""
            CREATE TABLE survey_schema AS
            SELECT * FROM read_csv_auto('{self.schema_csv_path}')
        """)

    def _create_star_schema(self) -> None:
        """Create star schema with fact and dimension tables."""
        # Create dimension table for questions
        self.conn.execute("""
            CREATE TABLE dim_questions AS
            SELECT 
                ROW_NUMBER() OVER (ORDER BY "column") as question_id,
                "column" as column_name,
                question_text,
                type
            FROM survey_schema
        """)

        # Create dimension table for respondents with demographic info
        # Using demographic columns that help identify respondent segments
        self.conn.execute("""
            CREATE TABLE dim_respondents AS
            SELECT 
                ROW_NUMBER() OVER (ORDER BY MainBranch, Age, Country) as respondent_id,
                MainBranch,
                Age,
                Employment,
                RemoteWork,
                Country,
                EdLevel,
                DevType,
                YearsCode,
                YearsCodePro,
                WorkExp,
                Industry
            FROM survey_data
        """)

        # Create fact table for responses - first handle SC questions, then MC questions separately
        self.conn.execute("""
            CREATE TABLE fact_responses AS
            WITH respondent_mapping AS (
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY MainBranch, Age, Country) as respondent_id,
                    *
                FROM survey_data
            ),
            question_mapping AS (
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY "column") as question_id,
                    "column" as column_name,
                    type
                FROM survey_schema
            ),
            -- Handle SC (Single Choice) questions
            sc_responses AS (
                SELECT 
                    r.respondent_id,
                    q.question_id,
                    CASE 
                        WHEN q.column_name = 'MainBranch' THEN r.MainBranch
                        WHEN q.column_name = 'Age' THEN r.Age
                        WHEN q.column_name = 'RemoteWork' THEN r.RemoteWork
                        WHEN q.column_name = 'Check' THEN r.Check
                        WHEN q.column_name = 'EdLevel' THEN r.EdLevel
                        WHEN q.column_name = 'YearsCode' THEN r.YearsCode
                        WHEN q.column_name = 'YearsCodePro' THEN r.YearsCodePro
                        WHEN q.column_name = 'DevType' THEN r.DevType
                        WHEN q.column_name = 'Country' THEN r.Country
                        WHEN q.column_name = 'SOVisitFreq' THEN r.SOVisitFreq
                        WHEN q.column_name = 'SOAccount' THEN r.SOAccount
                        WHEN q.column_name = 'AISelect' THEN r.AISelect
                        WHEN q.column_name = 'AISent' THEN r.AISent
                        WHEN q.column_name = 'WorkExp' THEN r.WorkExp
                        WHEN q.column_name = 'Industry' THEN r.Industry
                        ELSE NULL
                    END as answer_value
                FROM respondent_mapping r
                CROSS JOIN question_mapping q
                WHERE q.type = 'SC'
                AND CASE 
                    WHEN q.column_name = 'MainBranch' THEN r.MainBranch
                    WHEN q.column_name = 'Age' THEN r.Age
                    WHEN q.column_name = 'RemoteWork' THEN r.RemoteWork
                    WHEN q.column_name = 'Check' THEN r.Check
                    WHEN q.column_name = 'EdLevel' THEN r.EdLevel
                    WHEN q.column_name = 'YearsCode' THEN r.YearsCode
                    WHEN q.column_name = 'YearsCodePro' THEN r.YearsCodePro
                    WHEN q.column_name = 'DevType' THEN r.DevType
                    WHEN q.column_name = 'Country' THEN r.Country
                    WHEN q.column_name = 'SOVisitFreq' THEN r.SOVisitFreq
                    WHEN q.column_name = 'SOAccount' THEN r.SOAccount
                    WHEN q.column_name = 'AISelect' THEN r.AISelect
                    WHEN q.column_name = 'AISent' THEN r.AISent
                    WHEN q.column_name = 'WorkExp' THEN r.WorkExp
                    WHEN q.column_name = 'Industry' THEN r.Industry
                    ELSE NULL
                END IS NOT NULL
            )
            SELECT respondent_id, question_id, answer_value FROM sc_responses
        """)

        # Now handle MC questions by using string split and creating separate entries
        self.conn.execute("""
            INSERT INTO fact_responses
            SELECT DISTINCT
                r.respondent_id,
                q.question_id,
                TRIM(split_value) as answer_value
            FROM (
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY MainBranch, Age, Country) as respondent_id,
                    *
                FROM survey_data
            ) r
            CROSS JOIN (
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY "column") as question_id,
                    "column" as column_name,
                    type
                FROM survey_schema
                WHERE type = 'MC'
            ) q
            CROSS JOIN (
                SELECT UNNEST(string_split(
                    CASE 
                        WHEN q.column_name = 'Employment' THEN r.Employment
                        WHEN q.column_name = 'CodingActivities' THEN r.CodingActivities
                        WHEN q.column_name = 'LearnCode' THEN r.LearnCode
                        WHEN q.column_name = 'LearnCodeOnline' THEN r.LearnCodeOnline
                        WHEN q.column_name = 'TechDoc' THEN r.TechDoc
                        WHEN q.column_name = 'BuyNewTool' THEN r.BuyNewTool
                        WHEN q.column_name = 'TechEndorse' THEN r.TechEndorse
                        WHEN q.column_name = 'LanguageHaveWorkedWith' THEN r.LanguageHaveWorkedWith
                        WHEN q.column_name = 'LanguageWantToWorkWith' THEN r.LanguageWantToWorkWith
                        WHEN q.column_name = 'LanguageAdmired' THEN r.LanguageAdmired
                        WHEN q.column_name = 'DatabaseHaveWorkedWith' THEN r.DatabaseHaveWorkedWith
                        WHEN q.column_name = 'DatabaseWantToWorkWith' THEN r.DatabaseWantToWorkWith
                        WHEN q.column_name = 'DatabaseAdmired' THEN r.DatabaseAdmired
                        WHEN q.column_name = 'PlatformHaveWorkedWith' THEN r.PlatformHaveWorkedWith
                        WHEN q.column_name = 'PlatformWantToWorkWith' THEN r.PlatformWantToWorkWith
                        WHEN q.column_name = 'PlatformAdmired' THEN r.PlatformAdmired
                        WHEN q.column_name = 'WebframeHaveWorkedWith' THEN r.WebframeHaveWorkedWith
                        WHEN q.column_name = 'WebframeWantToWorkWith' THEN r.WebframeWantToWorkWith
                        WHEN q.column_name = 'WebframeAdmired' THEN r.WebframeAdmired
                        WHEN q.column_name = 'SOHow' THEN r.SOHow
                        WHEN q.column_name = 'AIBen' THEN r.AIBen
                        WHEN q.column_name = 'AIToolCurrently Using' THEN r."AIToolCurrently Using"
                        WHEN q.column_name = 'AIToolInterested in Using' THEN r."AIToolInterested in Using"
                        ELSE NULL
                    END, ';'
                )) as split_value
            ) s
            WHERE CASE 
                WHEN q.column_name = 'Employment' THEN r.Employment
                WHEN q.column_name = 'CodingActivities' THEN r.CodingActivities
                WHEN q.column_name = 'LearnCode' THEN r.LearnCode
                WHEN q.column_name = 'LearnCodeOnline' THEN r.LearnCodeOnline
                WHEN q.column_name = 'TechDoc' THEN r.TechDoc
                WHEN q.column_name = 'BuyNewTool' THEN r.BuyNewTool
                WHEN q.column_name = 'TechEndorse' THEN r.TechEndorse
                WHEN q.column_name = 'LanguageHaveWorkedWith' THEN r.LanguageHaveWorkedWith
                WHEN q.column_name = 'LanguageWantToWorkWith' THEN r.LanguageWantToWorkWith
                WHEN q.column_name = 'LanguageAdmired' THEN r.LanguageAdmired
                WHEN q.column_name = 'DatabaseHaveWorkedWith' THEN r.DatabaseHaveWorkedWith
                WHEN q.column_name = 'DatabaseWantToWorkWith' THEN r.DatabaseWantToWorkWith
                WHEN q.column_name = 'DatabaseAdmired' THEN r.DatabaseAdmired
                WHEN q.column_name = 'PlatformHaveWorkedWith' THEN r.PlatformHaveWorkedWith
                WHEN q.column_name = 'PlatformWantToWorkWith' THEN r.PlatformWantToWorkWith
                WHEN q.column_name = 'PlatformAdmired' THEN r.PlatformAdmired
                WHEN q.column_name = 'WebframeHaveWorkedWith' THEN r.WebframeHaveWorkedWith
                WHEN q.column_name = 'WebframeWantToWorkWith' THEN r.WebframeWantToWorkWith
                WHEN q.column_name = 'WebframeAdmired' THEN r.WebframeAdmired
                WHEN q.column_name = 'SOHow' THEN r.SOHow
                WHEN q.column_name = 'AIBen' THEN r.AIBen
                WHEN q.column_name = 'AIToolCurrently Using' THEN r."AIToolCurrently Using"
                WHEN q.column_name = 'AIToolInterested in Using' THEN r."AIToolInterested in Using"
                ELSE NULL
            END IS NOT NULL
            AND TRIM(split_value) != ''
            AND TRIM(split_value) != 'NA'
        """)

        # Create dimension table for answer options
        self.conn.execute("""
            CREATE TABLE dim_answer_options AS
            SELECT 
                ROW_NUMBER() OVER (ORDER BY question_id, answer_value) as answer_option_id,
                question_id,
                answer_value
            FROM (
                SELECT DISTINCT question_id, answer_value 
                FROM fact_responses
                WHERE answer_value IS NOT NULL AND answer_value != ''
            )
            ORDER BY question_id, answer_value
        """)

        # Update fact_responses to include answer_option_id
        self.conn.execute("""
            CREATE TABLE fact_responses_final AS
            SELECT 
                fr.respondent_id,
                fr.question_id,
                dao.answer_option_id,
                fr.answer_value
            FROM fact_responses fr
            JOIN dim_answer_options dao ON fr.question_id = dao.question_id 
                AND fr.answer_value = dao.answer_value
        """)

        # Drop intermediate table and rename final one
        self.conn.execute("DROP TABLE fact_responses")
        self.conn.execute("ALTER TABLE fact_responses_final RENAME TO fact_responses")

    def get_survey_structure(self) -> pd.DataFrame:
        """Display the survey structure (list of questions)."""
        return self.conn.execute("""
            SELECT 
                question_id,
                column_name,
                question_text,
                type,
                (SELECT COUNT(DISTINCT answer_value) 
                 FROM fact_responses fr 
                 WHERE fr.question_id = q.question_id) as num_answer_options
            FROM dim_questions q
            ORDER BY question_id
        """).fetchdf()

    def search_questions(self, search_term: str) -> pd.DataFrame:
        """Search for specific question or option."""
        return self.conn.execute(
            """
            SELECT DISTINCT
                q.question_id,
                q.column_name,
                q.question_text,
                q.type,
                dao.answer_value
            FROM dim_questions q
            LEFT JOIN dim_answer_options dao ON q.question_id = dao.question_id
            WHERE LOWER(q.question_text) LIKE LOWER(?)
                OR LOWER(q.column_name) LIKE LOWER(?)
                OR LOWER(dao.answer_value) LIKE LOWER(?)
            ORDER BY q.question_id, dao.answer_value
        """,
            [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"],
        ).fetchdf()

    def get_respondent_subset(
        self, question_column: str, answer_option: str
    ) -> pd.DataFrame:
        """Make respondents subsets based on question+option."""
        return self.conn.execute(
            """
            SELECT DISTINCT
                dr.respondent_id,
                dr.MainBranch,
                dr.Age,
                dr.Country,
                dr.DevType,
                dr.YearsCode
            FROM dim_respondents dr
            JOIN fact_responses fr ON dr.respondent_id = fr.respondent_id
            JOIN dim_questions dq ON fr.question_id = dq.question_id
            WHERE dq.column_name = ? 
                AND fr.answer_value = ?
            ORDER BY dr.respondent_id
        """,
            [question_column, answer_option],
        ).fetchdf()

    def get_answer_distribution(self, question_column: str) -> pd.DataFrame:
        """Display distribution of answers (shares) for SC and MC questions."""
        return self.conn.execute(
            """
            WITH answer_counts AS (
                SELECT 
                    fr.answer_value,
                    COUNT(*) as response_count,
                    dq.type
                FROM fact_responses fr
                JOIN dim_questions dq ON fr.question_id = dq.question_id
                WHERE dq.column_name = ?
                GROUP BY fr.answer_value, dq.type
            ),
            total_responses AS (
                SELECT 
                    COUNT(CASE WHEN dq.type = 'SC' THEN fr.respondent_id END) as total_sc,
                    COUNT(CASE WHEN dq.type = 'MC' THEN 1 END) as total_mc,
                    dq.type
                FROM fact_responses fr
                JOIN dim_questions dq ON fr.question_id = dq.question_id
                WHERE dq.column_name = ?
                GROUP BY dq.type
            )
            SELECT 
                ac.answer_value,
                ac.response_count,
                ac.type,
                ROUND(
                    ac.response_count * 100.0 / 
                    CASE WHEN ac.type = 'SC' THEN tr.total_sc ELSE tr.total_mc END, 2
                ) as percentage
            FROM answer_counts ac
            JOIN total_responses tr ON ac.type = tr.type
            ORDER BY ac.response_count DESC
        """,
            [question_column, question_column],
        ).fetchdf()

    def get_data_table(self) -> pd.DataFrame:
        """Return the survey data table."""
        return self.conn.execute("SELECT * FROM survey_data").fetchdf()

    def get_schema_table(self) -> pd.DataFrame:
        """Return the survey schema table."""
        return self.conn.execute("SELECT * FROM survey_schema").fetchdf()

    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """Get information about a table's structure."""
        return self.conn.execute(f"DESCRIBE {table_name}").fetchdf()

    def close(self) -> None:
        """Close the DuckDB connection."""
        if self.conn:
            self.conn.close()
