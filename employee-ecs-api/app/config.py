from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/employees"
    aws_region: str = "us-east-1"
    s3_export_bucket: str = ""
    s3_export_prefix: str = "exports/json/"
    sns_topic_arn: str = ""
    # Relative to project root / Docker WORKDIR, or absolute path
    employee_csv_path: str = "employee_data.csv"


settings = Settings()
