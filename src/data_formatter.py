"""
Data Formatter Module

Module for converting and formatting Excel data to JSON format
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataFormatter:
    """Data formatting class"""

    def __init__(self):
        self.date_formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
        ]

    def format_value(self, value: Any) -> Any:
        """Convert single value to JSON serializable format"""
        if value is None or pd.isna(value):
            return None

        # Handle numpy types
        if isinstance(value, (np.integer, np.floating)):
            return value.item()

        # Handle datetime
        if isinstance(value, (datetime, date)):
            return value.isoformat()

        # Handle pandas Timestamp
        if isinstance(value, pd.Timestamp):
            return value.isoformat()

        # Handle numpy datetime64
        if isinstance(value, np.datetime64):
            return pd.Timestamp(value).isoformat()

        # Other numpy types
        if isinstance(value, np.ndarray):
            return value.tolist()

        # Return basic types as is
        if isinstance(value, (int, float, str, bool)):
            return value

        # Convert other types to string
        try:
            return str(value)
        except Exception:
            return None

    def format_dataframe(
        self, df: pd.DataFrame, include_headers: bool = True
    ) -> Dict[str, Any]:
        """Convert DataFrame to JSON serializable dictionary"""
        try:
            # Convert NaN values to None
            df_clean = df.where(pd.notnull(df), None)

            if include_headers:
                # Use column names as headers
                headers = [str(col) for col in df_clean.columns]
                rows = []

                for _, row in df_clean.iterrows():
                    formatted_row = [self.format_value(val) for val in row]
                    rows.append(formatted_row)
            else:
                # Include index and columns
                headers = ["Index"] + [str(col) for col in df_clean.columns]
                rows = []

                for idx, row in df_clean.iterrows():
                    formatted_row = [self.format_value(idx)] + [
                        self.format_value(val) for val in row
                    ]
                    rows.append(formatted_row)

            # Collect data type information
            data_types = {}
            for col in df_clean.columns:
                dtype = str(df_clean[col].dtype)
                data_types[str(col)] = dtype

            return {
                "headers": headers,
                "rows": rows,
                "row_count": len(rows),
                "column_count": len(headers),
                "data_types": data_types,
            }

        except Exception as e:
            logger.error(f"DataFrame formatting failed: {e}")
            return {
                "headers": [],
                "rows": [],
                "row_count": 0,
                "column_count": 0,
                "data_types": {},
                "error": str(e),
            }

    def format_excel_data(
        self,
        file_path: str,
        worksheet_name: Optional[str] = None,
        max_rows: Optional[int] = None,
        include_headers: bool = True,
        data_only: bool = True,
    ) -> Dict[str, Any]:
        """Convert Excel file data to formatted JSON"""
        try:
            # Read Excel file using pandas
            if worksheet_name:
                df = pd.read_excel(
                    file_path, sheet_name=worksheet_name, engine="openpyxl"
                )
            else:
                df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl")

            # Decide whether to include only data
            if data_only:
                # Remove empty rows and columns
                df = df.dropna(how="all").dropna(axis=1, how="all")

            # Limit number of rows
            if max_rows and len(df) > max_rows:
                df = df.head(max_rows)

            # Format data
            formatted_data = self.format_dataframe(df, include_headers)

            return {
                "success": True,
                "file_path": file_path,
                "worksheet_name": worksheet_name or "Sheet1",
                "data": formatted_data,
                "max_rows_applied": max_rows,
                "include_headers": include_headers,
                "data_only": data_only,
            }

        except Exception as e:
            logger.error(f"Excel data formatting failed: {file_path} - {e}")
            return {
                "success": False,
                "error": f"Cannot format data: {str(e)}",
                "file_path": file_path,
            }

    def create_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate statistical summary information for DataFrame"""
        try:
            stats = {}

            # Basic information
            stats["total_rows"] = len(df)
            stats["total_columns"] = len(df.columns)

            # Statistics for each column
            column_stats = {}
            for col in df.columns:
                col_data = df[col].dropna()

                if len(col_data) == 0:
                    column_stats[col] = {
                        "data_type": str(df[col].dtype),
                        "null_count": len(df[col]),
                        "null_percentage": 100.0,
                        "unique_count": 0,
                    }
                    continue

                col_stats = {
                    "data_type": str(df[col].dtype),
                    "null_count": df[col].isnull().sum(),
                    "null_percentage": (df[col].isnull().sum() / len(df)) * 100,
                    "unique_count": col_data.nunique(),
                }

                # Additional statistics for numeric data
                if pd.api.types.is_numeric_dtype(col_data):
                    col_stats.update(
                        {
                            "min": col_data.min(),
                            "max": col_data.max(),
                            "mean": col_data.mean(),
                            "median": col_data.median(),
                            "std": col_data.std(),
                        }
                    )

                # Additional statistics for string data
                elif pd.api.types.is_string_dtype(col_data):
                    col_stats.update(
                        {
                            "min_length": col_data.str.len().min(),
                            "max_length": col_data.str.len().max(),
                            "avg_length": col_data.str.len().mean(),
                        }
                    )

                column_stats[col] = col_stats

            stats["columns"] = column_stats

            return stats

        except Exception as e:
            logger.error(f"Statistical summary generation failed: {e}")
            return {"error": str(e)}

    def format_search_results(
        self, matches: List[Dict[str, Any]], search_term: str, context_rows: int = 2
    ) -> Dict[str, Any]:
        """Format search results"""
        try:
            formatted_matches = []

            for match in matches:
                formatted_match = {
                    "row": match.get("row", 0),
                    "column": match.get("column", ""),
                    "cell_address": match.get("cell_address", ""),
                    "value": self.format_value(match.get("value", "")),
                    "context": {"before": [], "after": []},
                }

                # Add context information (to be implemented)
                # TODO: Include surrounding cell data

                formatted_matches.append(formatted_match)

            return {
                "search_term": search_term,
                "total_matches": len(formatted_matches),
                "matches": formatted_matches,
            }

        except Exception as e:
            logger.error(f"Search result formatting failed: {e}")
            return {
                "search_term": search_term,
                "total_matches": 0,
                "matches": [],
                "error": str(e),
            }

    def export_to_json(
        self,
        data: Dict[str, Any],
        output_path: Optional[str] = None,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> Dict[str, Any]:
        """Export data to JSON file"""
        try:
            json_str = json.dumps(
                data, indent=indent, ensure_ascii=ensure_ascii, default=str
            )

            if output_path:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(json_str)

                return {
                    "success": True,
                    "output_path": output_path,
                    "file_size": len(json_str.encode("utf-8")),
                }
            else:
                return {
                    "success": True,
                    "json_data": json_str,
                    "data_size": len(json_str.encode("utf-8")),
                }

        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            return {"success": False, "error": str(e)}


# Convenience functions
def format_excel_data(
    file_path: str,
    worksheet_name: Optional[str] = None,
    max_rows: Optional[int] = None,
    include_headers: bool = True,
) -> Dict[str, Any]:
    """Convenience function to format Excel data"""
    formatter = DataFormatter()
    return formatter.format_excel_data(
        file_path, worksheet_name, max_rows, include_headers
    )


def create_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Convenience function to generate DataFrame statistical summary"""
    formatter = DataFormatter()
    return formatter.create_summary_stats(df)


def export_to_json(
    data: Dict[str, Any], output_path: Optional[str] = None
) -> Dict[str, Any]:
    """Convenience function to export data to JSON"""
    formatter = DataFormatter()
    return formatter.export_to_json(data, output_path)
