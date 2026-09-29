"""Clean the raw CSV, calculate metrics, and write the business report."""

from src.business_analysis import add_business_metrics, write_business_report
from src.data_cleaner import clean_data
from src.data_loader import PROJECT_ROOT, load_data


def main() -> None:
    raw_data = load_data()
    cleaned = clean_data(raw_data)
    enriched = add_business_metrics(cleaned)
    cleaned_path = PROJECT_ROOT / "data" / "cleaned" / "logistics_cleaned.csv"
    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(cleaned_path, index=False, date_format="%Y-%m-%d")

    report_path = PROJECT_ROOT / "reports" / "business_report.md"
    write_business_report(
        enriched,
        raw_rows=len(raw_data),
        report_path=report_path,
        raw_data=raw_data,
    )

    print(f"Raw rows: {len(raw_data):,}")
    print(f"Cleaned rows: {len(cleaned):,}")
    print(f"Removed rows: {len(raw_data) - len(cleaned):,}")
    print(f"Cleaned CSV: {cleaned_path}")
    print(f"Business report: {report_path}")


if __name__ == "__main__":
    main()